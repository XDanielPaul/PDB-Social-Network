import json
from typing import Annotated, Any

from litestar import MediaType, Request, delete, get, post, put
from litestar.contrib.jwt import Token
from litestar.controller import Controller
from litestar.datastructures import UploadFile
from litestar.dto import DTOData
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post_model import (
    PartialPostDto,
    PartialPostReturnDto,
    Post,
    PostCreate,
    PostReturnModel,
)
from app.models.tag_model import Tag, tags_posts_associations
from app.models.user_model import User
from app.utils.pika import RabbitMQConnection


class PostController(Controller):
    path = "/posts"

    @post('/', tags=["Posts"], dto=PartialPostDto)
    async def create_post(
        self,
        request: Request[User, Token, Any],
        data: DTOData[PostCreate],
        db_session: AsyncSession,
    ) -> dict:
        data_dct = data.create_instance()
        db_user = await db_session.get(User, request.auth.sub)

        if not db_user:
            raise HTTPException(
                detail="User which creates the post doesnt exist.", status_code=HTTP_404_NOT_FOUND
            )
        tags_from_db: list[Tag] = []
        for tag in data_dct.tags:
            db_request = await db_session.execute(select(Tag).filter(Tag.name == tag.name))
            tag_db = db_request.scalars().first()
            if tag_db:
                # tag already exists -> just add the connection
                tags_from_db.append(tag_db)
            else:
                new_tag = Tag(name=tag.name)
                db_session.add(new_tag)
                await db_session.commit()
                await db_session.refresh(new_tag)
                tags_from_db.append(new_tag)

        post_without_tags = data_dct.model_dump()
        del post_without_tags['tags']
        db_post = Post(**(post_without_tags))
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

        for tag in tags_from_db:
            insert_statement = tags_posts_associations.insert().values(
                {'tag_name': tag.id, 'tag_post': db_post.id}
            )
            await db_session.execute(insert_statement)
        await db_session.commit()
        print(data_for_rabbit)
        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', db_post.format_for_rabbit('CREATE'))
            conn.publish_message('tags', data_for_rabbit)

        return {'return': True}
