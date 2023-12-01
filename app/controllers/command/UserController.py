import json
from typing import Any, Optional
from uuid import UUID

from litestar import Request, Response, delete, post, put
from litestar.connection import ASGIConnection
from litestar.contrib.jwt import JWTAuth, Token
from litestar.controller import Controller
from litestar.dto import DTOData
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from sqlalchemy import and_, select
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
    user_followers_association,
)
from app.utils.pika import RabbitMQConnection


# Authentication handler which returns user object based on jwt token
async def retrieve_user_handler(
    token: Token, connection: ASGIConnection[Any, Any, Any, Any]
) -> Optional[User]:
    async with connection.app.state.db_engine.begin() as db_conn:
        result = await db_conn.execute(select(User).where(User.id == token.sub))
        user = result.scalar_one_or_none()

    if not user:
        return None
    return user


# JWT authentication object
jwt_auth = JWTAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret="secret",
    exclude=['/schema', '/users/login', '/users/register'],
)


# User controller for CUD operations
class UserController(Controller):
    path = "/users"

    # Create a user
    @post(path="/register", dto=PartialUserDto, tags=["User"])
    async def create_user(
        self, data: DTOData[UserCreateModel], db_session: AsyncSession
    ) -> UserReturn:
        # Check if user already exists
        user_to_create = data.create_instance().model_dump()

        # Check if user already exists
        check_if_exists = await db_session.execute(
            select(User).filter(User.username == user_to_create['username'])
        )

        if check_if_exists.scalars().first():
            raise HTTPException(
                detail="This user is already in the database.", status_code=HTTP_409_CONFLICT
            )
        # Create the user
        created_user = User(**user_to_create)
        created_user.generate_hash_password(created_user.password)
        print(created_user.password)
        db_session.add(created_user)
        await db_session.commit()
        await db_session.refresh(created_user)

        # Publish the user to RabbitMQ queue for mongo synchronization
        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', created_user.format_for_rabbit('CREATE'))

        return UserReturn(**(created_user.to_dict()))

    # Update a user
    @put(path="/", dto=UserReturnDto, tags=["User"])
    async def update_user(self, data: DTOData[UserReturn], db_session: AsyncSession) -> UserReturn:
        # Check if user exists
        data_dct = data.create_instance().model_dump()
        db_user = await db_session.get(User, data_dct['id'])
        if not db_user:
            raise HTTPException(
                detail="User with this id doesn't exist.", status_code=HTTP_404_NOT_FOUND
            )
        # Update the user
        db_user.username = data_dct.get('username', db_user.username)
        db_user.profile_picture = data_dct.get('profile_picture', db_user.profile_picture)
        db_user.profile_bio = data_dct.get('profile_bio', db_user.profile_bio)
        await db_session.commit()
        await db_session.refresh(db_user)
        # Send the user to RabbitMQ queue for mongo synchronization
        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', db_user.format_for_rabbit('UPDATE'))

        return UserReturn(**(db_user.to_dict()))

    # Delete a user
    @delete(path="/{id:uuid}", status_code=200, tags=["User"])
    async def delete_user(self, id: UUID, db_session: AsyncSession) -> DeleteConfirm:
        # Check if user exists
        db_user = await db_session.get(User, id)
        if not db_user:
            raise HTTPException(
                detail="User with this id doesn't exist.", status_code=HTTP_404_NOT_FOUND
            )
        # Send the message to RabbitMQ queue for mongo synchronization
        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', db_user.format_for_rabbit('DELETE'))
        await db_session.delete(db_user)
        await db_session.commit()

        return DeleteConfirm(deleted=True, message=f"User with id [{id}] was deleted.")

    # Login a user
    @post(path="/login", dto=PartiaUserLoginDto, tags=["User"])
    async def login(self, data: DTOData[UserLogin], db_session: AsyncSession) -> Response[User]:
        # Check if user exists
        user_to_login = data.create_instance().model_dump()
        result = await db_session.execute(
            select(User).where(User.username == user_to_login['username'])
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            raise HTTPException(
                detail="Username or password is not correct.", status_code=HTTP_404_NOT_FOUND
            )
        # Check if password is correct
        if not db_user.verify_password(user_to_login['password']):
            raise HTTPException(
                detail="Username or password is not correct.", status_code=HTTP_404_NOT_FOUND
            )
        # Send a jwt token as a response
        response = jwt_auth.login(
            identifier=str(db_user.id),
            send_token_as_response_body=True,
        )
        return response

    # Follow a user
    @post(path="/follow/{id:uuid}", tags=["User"])
    async def follow_user(
        self, request: Request[User, Token, Any], id: UUID, follow: bool, db_session: AsyncSession
    ) -> dict:
        # Check if user exists
        user_to_follow = await db_session.get(User, id)
        if not user_to_follow:
            raise HTTPException(
                detail="User with this id doesn't exist.", status_code=HTTP_404_NOT_FOUND
            )

        if user_to_follow.id == request.auth.sub:
            raise HTTPException(detail="You cannot follow yourself.", status_code=HTTP_409_CONFLICT)
        # Check if user is already following the user
        check_if_following = await db_session.execute(
            select(user_followers_association)
            .filter(user_followers_association.c.follower_id == request.auth.sub)
            .filter(user_followers_association.c.followed_id == user_to_follow.id)
        )
        if follow:
            if bool(check_if_following.scalars().first()):
                raise HTTPException(
                    detail="You are already following this user.", status_code=HTTP_409_CONFLICT
                )
            # Follow the user
            insert_statement = user_followers_association.insert().values(
                {'follower_id': request.auth.sub, 'followed_id': user_to_follow.id}
            )
            await db_session.execute(insert_statement)
            await db_session.commit()
        else:
            if not bool(check_if_following.scalars().first()):
                raise HTTPException(
                    detail="You are not following the user.", status_code=HTTP_409_CONFLICT
                )
            # Unfollow the user
            delete_statement = user_followers_association.delete().where(
                and_(
                    user_followers_association.c.follower_id == request.auth.sub,
                    user_followers_association.c.followed_id == user_to_follow.id,
                )
            )
            await db_session.execute(delete_statement)
            await db_session.commit()

        data_for_rabbit = json.dumps(
            {
                'follower_id': str(request.auth.sub),
                'followed_id': str(user_to_follow.id),
                'method': 'ADD' if follow else 'REMOVE',
            }
        )
        # Publish the message to RabbitMQ queue for mongo synchronization
        with RabbitMQConnection() as conn:
            conn.publish_message('follow_user', data_for_rabbit)

        return {"followed": follow}
