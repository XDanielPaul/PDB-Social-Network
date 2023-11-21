import json
from typing import Any, Optional
from uuid import UUID

from litestar import Response, delete, get, post, put
from litestar.connection import ASGIConnection
from litestar.contrib.jwt import JWTAuth, Token
from litestar.controller import Controller
from litestar.dto import DTOData
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base_for_modelling import DeleteConfirm
from app.models.user_model import (
    PartialUserDto,
    PartiaUserLoginDto,
    User,
    UserCreateModel,
    UserLogin,
    UserReturn,
    UserReturnDto,
)
from app.utils.pika import RabbitMQConnection


# Authentication
async def retrieve_user_handler(
    token: Token, connection: ASGIConnection[Any, Any, Any, Any]
) -> Optional[User]:
    async with connection.app.state.db_engine.begin() as db_conn:
        result = await db_conn.execute(select(User).where(User.id == token.sub))
        user = result.scalar_one_or_none()

    if not user:
        return None
    return user


jwt_auth = JWTAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret="secret",
    exclude=['/schema', '/users/login', '/users/register'],
)


class UserController(Controller):
    path = "/users"

    @get(path="/", tags=["User"])
    async def get_users(self, db_session: AsyncSession) -> list[UserReturn]:
        request = await db_session.execute(select(User))
        return [UserReturn(**(user.to_dict())) for user in request.scalars().all()]

    @get(path="/{id:uuid}", tags=["User"])
    async def get_user(self, id: UUID, db_session: AsyncSession) -> UserReturn:
        user = await db_session.get(User, id)

        if not user:
            raise HTTPException(
                detail="User with this id does not exist", status_code=HTTP_404_NOT_FOUND
            )
        return UserReturn(**(user.to_dict()))

    @post(path="/register", dto=PartialUserDto, tags=["User"])
    async def create_user(
        self, data: DTOData[UserCreateModel], db_session: AsyncSession
    ) -> UserReturn:
        user_to_create = data.create_instance().model_dump()

        check_if_exists = await db_session.execute(
            select(User).filter(User.username == user_to_create['username'])
        )

        print(user_to_create)
        if check_if_exists.scalars().first():
            raise HTTPException(
                detail="This user is already in the database.", status_code=HTTP_409_CONFLICT
            )
        created_user = User(**user_to_create)
        db_session.add(created_user)
        await db_session.commit()
        await db_session.refresh(created_user)

        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', created_user.format_for_rabbit('CREATE'))

        return UserReturn(**(created_user.to_dict()))

    @put(path="/", dto=UserReturnDto, tags=["User"])
    async def update_user(self, data: DTOData[UserReturn], db_session: AsyncSession) -> UserReturn:
        data_dct = data.create_instance().model_dump()
        db_user = await db_session.get(User, data_dct['id'])
        if not db_user:
            raise HTTPException(
                detail="User with this id doesn't exist.", status_code=HTTP_404_NOT_FOUND
            )
        db_user.username = data_dct.get('username', db_user.username)
        db_user.profile_picture = data_dct.get('username', db_user.profile_picture)
        db_user.profile_bio = data_dct.get('username', db_user.profile_bio)
        await db_session.commit()
        await db_session.refresh(db_user)
        return UserReturn(**(db_user.to_dict()))

    @delete(path="/{id:uuid}", status_code=200, tags=["User"])
    async def delete_user(self, id: UUID, db_session: AsyncSession) -> DeleteConfirm:
        db_user = await db_session.get(User, id)
        if not db_user:
            raise HTTPException(
                detail="User with this id doesn't exist.", status_code=HTTP_404_NOT_FOUND
            )
        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', db_user.format_for_rabbit('DELETE'))
        await db_session.delete(db_user)
        await db_session.commit()

        return DeleteConfirm(deleted=True, message=f"User with id [{id}] was deleted.")

    @post(path="/login", dto=PartiaUserLoginDto, tags=["User"])
    async def login(self, data: DTOData[UserLogin], db_session: AsyncSession) -> Response[User]:
        user_to_login = data.create_instance().model_dump()
        result = await db_session.execute(
            select(User).where(User.username == user_to_login['username'])
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            raise HTTPException(
                detail="User with this username doesn't exist.", status_code=HTTP_404_NOT_FOUND
            )
        if db_user.password != user_to_login['password']:
            raise HTTPException(detail="Wrong password.", status_code=HTTP_404_NOT_FOUND)

        response = jwt_auth.login(
            identifier=str(db_user.id),
            send_token_as_response_body=True,
        )
        return response
