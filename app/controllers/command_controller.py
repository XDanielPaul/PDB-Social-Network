import os
import sys
from uuid import UUID

from litestar import Litestar, delete, get, post, put
from litestar.contrib.sqlalchemy.base import UUIDBase
from litestar.contrib.sqlalchemy.plugins.init import SQLAlchemyInitPlugin
from litestar.contrib.sqlalchemy.plugins.init.config import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
)
from litestar.controller import Controller
from litestar.di import Provide
from litestar.status_codes import HTTP_200_OK
from sqlalchemy.ext.asyncio import AsyncSession

# TODO: Fix imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ..models.command_model import ReadDTO, UserModel, UserRepository, WriteDTO
from ..utils.controller import Service
from ..utils.pika import RabbitMQConnection


@get("/")
async def hello_world() -> str:
    # Publish the message to the 'hello' queue
    with RabbitMQConnection() as conn:
        conn.publish_message('hello', {'message': 'Hello from Controller!'})
    return "Hello, Controller!"


# Service dependency
def provides_service(db_session: AsyncSession) -> Service:
    """Constructs repository and service objects for the request."""
    return Service(UserRepository(session=db_session))


# UserModel controller which handles requests for /users
class UserController(Controller):
    # Dependency injection
    dto = WriteDTO
    return_dto = ReadDTO
    dependencies = {"service": Provide(provides_service, sync_to_thread=False)}

    @get(path="/users")
    async def get_users(self, service: Service) -> list[UserModel]:
        return await service.list()

    @get(path="/users/{user_id:uuid}")
    async def get_user(self, service: Service, user_id: UUID) -> UserModel:
        return await service.get(user_id)

    @post(path="/users")
    async def create_user(self, service: Service, data: UserModel) -> UserModel:
        new_user = await service.create(data)
        await service.repository.session.commit()
        with RabbitMQConnection() as conn:
            conn.publish_message('hello', UserModel.to_dict(new_user, 'post'))

        return new_user

    @put(path="/users/{user_id:uuid}")
    async def update_user(self, data: UserModel, service: Service, user_id: UUID) -> UserModel:
        updated_user = await service.update(user_id, data)
        await service.repository.session.commit()
        with RabbitMQConnection() as conn:
            conn.publish_message('hello', UserModel.to_dict(updated_user, 'put'))
        return updated_user

    @delete(path="/users/{user_id:uuid}", status_code=HTTP_200_OK)
    async def delete_user(self, service: Service, user_id: UUID) -> UserModel:
        deleted_user = await service.delete(user_id)
        await service.repository.session.commit()
        with RabbitMQConnection() as conn:
            conn.publish_message('hello', UserModel.to_dict(deleted_user, 'delete'))
        return deleted_user


session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///test.sqlite", session_config=session_config
)  # Create 'async_session' dependency.
sqlalchemy_plugin = SQLAlchemyInitPlugin(config=sqlalchemy_config)


async def on_startup() -> None:
    """Initializes the database."""
    async with sqlalchemy_config.get_engine().begin() as conn:
        await conn.run_sync(UUIDBase.metadata.create_all)


app = Litestar(
    route_handlers=[hello_world, UserController],
    on_startup=[on_startup],
    plugins=[SQLAlchemyInitPlugin(config=sqlalchemy_config)],
)
