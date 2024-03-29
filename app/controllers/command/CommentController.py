import json
from typing import Any
from uuid import UUID

from litestar import Request, delete, post, put
from litestar.contrib.jwt import Token
from litestar.controller import Controller
from litestar.dto import DTOData
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base_for_modelling import DeleteConfirm
from app.models.comment_model import (
    Comment,
    CommentCreate,
    PartialCommentDto,
    PartialUpdateCommentDto,
    UpdateComment,
)
from app.models.post_model import Post
from app.models.user_model import User
from app.utils.pika import RabbitMQConnection


# Comment controller for CUD operations
class CommentController(Controller):
    path = "/comments"

    # Create a comment
    @post('/', tags=["Comments"], dto=PartialCommentDto)
    async def create_comment(
        self,
        request: Request[User, Token, Any],
        data: DTOData[CommentCreate],
        db_session: AsyncSession,
    ) -> dict:
        # Get the data from the DTO
        data_dct = data.create_instance()
        # Get the user from the database
        db_user = await db_session.get(User, request.auth.sub)

        if not db_user:
            raise HTTPException(
                detail="User which creates the comment does not exist.",
                status_code=HTTP_404_NOT_FOUND,
            )
        # Get the post from the database
        db_post = await db_session.get(Post, data_dct.on_post_id)

        if not db_post:
            raise HTTPException(
                detail="Post on which the comment is created does not exist.",
                status_code=HTTP_404_NOT_FOUND,
            )

        # Create the comment
        comment = data_dct.model_dump()
        db_comment = Comment(**comment, on_post=db_post, created_comment_by=db_user)
        db_session.add(db_comment)
        db_post.comments.append(db_comment)

        db_session.add(db_post)
        await db_session.commit()
        await db_session.refresh(db_comment)

        # Data for RabbitMQ regarding the comment and the post relation
        data_for_rabbit = json.dumps(
            {'post_id': str(db_post.id), 'comment_id': str(db_comment.id), 'method': 'ADD'}
        )

        # Publish the message to the queue for Mongo synchronization
        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', db_comment.format_for_rabbit('CREATE'))
            conn.publish_message('comments', data_for_rabbit)

        return {'Comment': db_comment.to_dict_create()}

    # Update a comment
    @put(path='/', dto=PartialUpdateCommentDto, tags=["Comments"])
    async def update_comment(
        self,
        data: DTOData[UpdateComment],
        db_session: AsyncSession,
    ) -> dict:
        data_dct = data.create_instance().model_dump()
        db_comment = await db_session.get(Comment, data_dct['id'])

        if not db_comment:
            raise HTTPException(
                detail="Comment with this id does not exist", status_code=HTTP_404_NOT_FOUND
            )

        db_comment.content = data_dct['content']
        await db_session.commit()
        await db_session.refresh(db_comment)

        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', db_comment.format_for_rabbit('UPDATE'))

        return {'return': True}

    # Delete a comment
    @delete(path="/{id:uuid}", status_code=200, tags=["Comments"])
    async def delete_comment(self, id: UUID, db_session: AsyncSession) -> DeleteConfirm:
        db_comment = await db_session.get(Comment, id)
        if not db_comment:
            raise HTTPException(
                detail="Comment with this id does not exist", status_code=HTTP_404_NOT_FOUND
            )

        db_post = await db_session.get(Post, db_comment.on_post_id)

        await db_session.delete(db_comment)
        await db_session.commit()

        # Data for rabbitMQ regarding the comment and the post relation
        data_for_rabbit = json.dumps(
            {'post_id': str(db_post.id), 'comment_id': str(db_comment.id), 'method': 'REMOVE'}
        )

        # Publish the message to the queue for Mongo synchronization
        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', db_comment.format_for_rabbit('DELETE'))
            conn.publish_message('comments', data_for_rabbit)

        return DeleteConfirm(deleted=True, message=f"Comment with id {id} was deleted.")
