import json
from typing import Any
from uuid import UUID

from litestar import Request, delete, post
from litestar.contrib.jwt import Token
from litestar.controller import Controller
from litestar.dto import DTOData
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.base_for_modelling import DeleteConfirm
from app.models.like_dislike_model import LikeDislike
from app.models.post_model import (
    LikeDislikeModel,
    PartialPostDto,
    Post,
    PostCreate,
    PostLikeDislike,
    PostLikeDislikeDto,
    PostReturnModel,
    TagInPost,
    posts_shared_association,
)
from app.models.tag_model import Tag, tags_posts_associations
from app.models.user_model import User
from app.utils.pika import RabbitMQConnection


# Post controller for CUD operations
class PostController(Controller):
    path = "/posts"

    # Create post
    @post('/', tags=["Posts"], dto=PartialPostDto)
    async def create_post(
        self,
        request: Request[User, Token, Any],
        data: DTOData[PostCreate],
        db_session: AsyncSession,
    ) -> PostReturnModel:
        # Get the data from the DTO
        data_dct = data.create_instance()

        # Get the user from the database
        db_user = await db_session.get(User, request.auth.sub)

        if not db_user:
            raise HTTPException(
                detail="User which creates the post doesnt exist.", status_code=HTTP_404_NOT_FOUND
            )
        # Check if the tags already exist in the database
        tags_from_db: list[Tag] = []
        for tag in data_dct.tags:
            db_request = await db_session.execute(select(Tag).filter(Tag.name == tag.name))
            tag_db = db_request.scalars().first()
            if tag_db:
                # tag already exists -> just add the connection
                tags_from_db.append(tag_db)
            else:
                # tag doesnt exist -> create it and add the connection
                new_tag = Tag(name=tag.name)
                db_session.add(new_tag)
                await db_session.commit()
                await db_session.refresh(new_tag)
                tags_from_db.append(new_tag)

        # Create the post
        post_without_tags = data_dct.model_dump()
        del post_without_tags['tags']
        db_post = Post(**(post_without_tags), created_by=db_user)
        db_session.add(db_post)
        await db_session.commit()
        await db_session.refresh(db_post)

        data_for_rabbit = json.dumps(
            {
                'post_id': str(db_post.id),
                'tags': [tag.format_for_rabbit('ADD') for tag in tags_from_db],
                'method': 'ADD',
            }
        )

        # Add the tags to the post
        for tag in tags_from_db:
            insert_statement = tags_posts_associations.insert().values(
                {'tag_name': tag.id, 'tag_post': db_post.id}
            )
            await db_session.execute(insert_statement)
        await db_session.commit()

        # Publish the message to the RabbitMQ queue for Mongo synchronization
        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', db_post.format_for_rabbit('CREATE'))
            conn.publish_message('tags', data_for_rabbit)
            conn.publish_message(
                'posts',
                json.dumps(
                    {'method': 'ADD', 'user_id': str(db_user.id), 'post_id': str(db_post.id)}
                ),
            )

        return PostReturnModel(
            title=db_post.title,
            content=db_post.content,
            tags=[TagInPost(name=tag.name) for tag in tags_from_db],
            id=db_post.id,
        )

    # Delete post
    @delete('/{post_id:uuid}', tags=["Posts"], status_code=200)
    async def delete_post(
        self, request: Request[User, Token, Any], post_id: UUID, db_session: AsyncSession
    ) -> DeleteConfirm:
        # Check if post exists
        db_request = await db_session.execute(
            select(Post).filter(Post.id == post_id).options(selectinload(Post.tagged))
        )
        post = db_request.scalars().first()
        tags: list[Tag] = post.tagged
        # Check if the user is the creator of the post
        if post.created_by_id == request.auth.sub:
            raise HTTPException(
                detail="You dont have access rights to do this.", status_code=HTTP_401_UNAUTHORIZED
            )
        # Delete the post
        await db_session.delete(post)
        await db_session.commit()

        # Publish the message to the RabbitMQ queue for Mongo synchronization
        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', post.format_for_rabbit('DELETE'))
            conn.publish_message(
                'posts',
                json.dumps(
                    {'method': 'REMOVE', 'user_id': str(request.auth.sub), 'post_id': str(post.id)}
                ),
            )

        return DeleteConfirm(deleted=True, message="Post was deleted")

    # Like or dislike post
    @post('/like-dislike', dto=PostLikeDislikeDto, tags=["Posts"])
    async def like_dislike_post(
        self,
        request: Request[User, Token, Any],
        data: DTOData[PostLikeDislike],
        db_session: AsyncSession,
    ) -> LikeDislikeModel:
        # Get the data from the DTO
        data_model = data.create_instance()

        # Get the user from the database
        db_user = await db_session.get(User, request.auth.sub)
        if not db_user:
            raise HTTPException(
                detail="User which wants to add review doesnt exist.",
                status_code=HTTP_404_NOT_FOUND,
            )
        # Get the post from the database
        db_post = await db_session.get(Post, data_model.post_id)
        if not db_post:
            raise HTTPException(detail="Post doesn't exist", status_code=HTTP_404_NOT_FOUND)
        # Check if the user already reviewed this post
        db_like_dislike = await db_session.execute(
            select(LikeDislike)
            .filter(LikeDislike.reviewed_by_id == db_user.id)
            .filter(LikeDislike.reviewed_on_id == db_post.id)
        )
        check_like_dislike = db_like_dislike.scalars().first()
        if check_like_dislike:
            raise HTTPException(
                detail="This user already reviewed this post.", status_code=HTTP_409_CONFLICT
            )
        # Create the review
        new_review = LikeDislike(
            review_type=data_model.like, reviewed_by_id=db_user.id, reviewed_on_id=db_post.id
        )
        db_session.add(new_review)
        await db_session.commit()
        await db_session.refresh(new_review)
        # Publish the message to the RabbitMQ queue for Mongo synchronization
        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', new_review.format_for_rabbit('CREATE'))
        return LikeDislikeModel(user_id=db_user.id, post_id=db_post.id, review_type=data_model.like)

    # Delete like or dislike
    @delete(
        '/like-dislike/{post_id:uuid}',
        tags=["Posts"],
        status_code=200,
    )
    async def like_dislike_delete(
        self,
        request: Request[User, Token, Any],
        post_id: UUID,
        db_session: AsyncSession,
    ) -> DeleteConfirm:
        # Check if user reviewed this post
        db_check = await db_session.execute(
            select(LikeDislike)
            .filter(LikeDislike.reviewed_by_id == request.auth.sub)
            .filter(LikeDislike.reviewed_on_id == post_id)
        )
        like_dislike_instance = db_check.scalars().first()
        if not like_dislike_instance:
            raise HTTPException(detail="Review doesn't exist", status_code=HTTP_404_NOT_FOUND)

        # Delete the review
        await db_session.delete(like_dislike_instance)
        await db_session.commit()

        # Publish the message to the RabbitMQ queue for Mongo synchronization
        with RabbitMQConnection() as conn:
            conn.publish_message(
                'crud_operations', like_dislike_instance.format_for_rabbit('DELETE')
            )

        return DeleteConfirm(deleted=True, message="Review was deleted.")

    # Share post
    @post('/share/{id:uuid}', tags=["Posts"], dto=PartialPostDto)
    async def share_post(
        self,
        request: Request[User, Token, Any],
        id: UUID,
        share: bool,
        db_session: AsyncSession,
    ) -> dict:
        # Get the user from the database
        db_user = await db_session.get(User, request.auth.sub)

        if not db_user:
            raise HTTPException(
                detail="User which wants to share the post doesnt exist.",
                status_code=HTTP_404_NOT_FOUND,
            )

        # Get the post from the database
        db_post = await db_session.get(Post, id)

        if not db_post:
            raise HTTPException(
                detail="Post which you want to share doesnt exist.",
                status_code=HTTP_404_NOT_FOUND,
            )

        if share:
            # Check if user already shared this post
            if db_user in db_post.shared_by_users:
                raise HTTPException(
                    detail="You already shared this post.", status_code=HTTP_409_CONFLICT
                )
            # Share the post
            insert_statement = posts_shared_association.insert().values(
                {'shared_by': db_user.id, 'shared_post': db_post.id}
            )
            await db_session.execute(insert_statement)
            await db_session.commit()

        else:
            # Check if user shared this post
            if db_user not in db_post.shared_by_users:
                raise HTTPException(
                    detail="You didn't share this post.", status_code=HTTP_409_CONFLICT
                )

            # Unshare the post
            delete_statement = posts_shared_association.delete().where(
                and_(
                    posts_shared_association.c.shared_by == db_user.id,
                    posts_shared_association.c.shared_post == db_post.id,
                )
            )
            await db_session.execute(delete_statement)
            await db_session.commit()

        data_for_rabbit = json.dumps(
            {
                'post_id': str(db_post.id),
                'user_id': str(db_user.id),
                'method': 'ADD' if share else 'REMOVE',
            }
        )

        # Publish the message to the RabbitMQ queue for Mongo synchronization
        with RabbitMQConnection() as conn:
            conn.publish_message('share_post', data_for_rabbit)

        return {'return': True}
