from litestar import delete, get, post, put
from uuid import UUID
from litestar.controller import Controller
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from sqlalchemy.ext.asyncio import AsyncSession
from litestar.dto import DTOData
from sqlalchemy import select
from litestar.exceptions import HTTPException
from app.utils.pika import RabbitMQConnection
from app.models.user_model import UserModel, UserCreateModel, PartialUserDto, UserReturn, UserReturnDto
from app.models.base_for_modelling import DeleteConfirm
import json

class UserController(Controller):

    path = "/users"

    @get(path="/", tags=["User"])
    async def get_users(self,  db_session: AsyncSession) -> list[UserReturn]:
        request = await db_session.execute(select(UserModel))
        return [UserReturn(**(user.to_dict())) for user in request.scalars().all()]

    @get(path="/{id:uuid}", tags=["User"])
    async def get_user(self, id: UUID, db_session: AsyncSession) -> UserReturn:
        user = await db_session.get(UserModel, id)

        if not user:
            raise HTTPException(
                detail="User with this id does not exist", status_code=HTTP_404_NOT_FOUND)
        return UserReturn(**(user.to_dict()))

    @post(path="/", dto=PartialUserDto, tags=["User"])
    async def create_user(self, data: DTOData[UserCreateModel], db_session: AsyncSession) -> UserReturn:
        user_to_create = data.create_instance().model_dump()
        check_if_exists = await db_session.execute(select(UserModel).filter(UserModel.username == user_to_create['username']))
        if check_if_exists.scalars().first():
            raise HTTPException(
                detail="This user is already in the database.", status_code=HTTP_409_CONFLICT)
        created_user = UserModel(**user_to_create)
        db_session.add(created_user)
        await db_session.commit()
        await db_session.refresh(created_user)

        with RabbitMQConnection() as conn:
            conn.publish_message('user',created_user.format_for_rabbit('CREATE'))

        return UserReturn(**(created_user.to_dict()))

    @put(path="/", dto=UserReturnDto, tags=["User"])
    async def update_user(self, data: DTOData[UserReturn], db_session: AsyncSession) -> UserReturn:
        data_dct = data.create_instance().model_dump()
        db_user = await db_session.get(UserModel, data_dct['id'])
        if not db_user:
            raise HTTPException(
                detail="User with this id doesn't exist.", status_code=HTTP_404_NOT_FOUND)
        db_user.username = data_dct.get('username', db_user.username)
        db_user.profile_picture = data_dct.get(
            'username', db_user.profile_picture)
        db_user.profile_bio = data_dct.get('username', db_user.profile_bio)
        await db_session.commit()
        await db_session.refresh(db_user)
        return UserReturn(**(db_user.to_dict()))

    @delete(path="/{id:uuid}", status_code=200, tags=["User"])
    async def delete_user(self, id: UUID, db_session: AsyncSession) -> DeleteConfirm:
        db_user = await db_session.get(UserModel, id)
        if not db_user:
            raise HTTPException(
                detail="User with this id doesn't exist.", status_code=HTTP_404_NOT_FOUND)
        with RabbitMQConnection() as conn:
            conn.publish_message('user',db_user.format_for_rabbit('DELETE'))
        await db_session.delete(db_user)
        await db_session.commit()

        return DeleteConfirm(
            deleted=True,
            message=f"User with id [{id}] was deleted."
        )
