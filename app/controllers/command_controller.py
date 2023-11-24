from typing import Any

from litestar import Litestar, Request, get
from litestar.contrib.jwt import Token
from litestar.contrib.sqlalchemy.base import UUIDBase
from litestar.contrib.sqlalchemy.plugins.init import SQLAlchemyInitPlugin
from litestar.contrib.sqlalchemy.plugins.init.config import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
)
from litestar.openapi.config import OpenAPIConfig

from app.controllers.command.CommentController import CommentController
from app.controllers.command.PostController import PostController
from app.controllers.command.TagController import TagController
from app.controllers.command.UserController import UserController, jwt_auth
from app.controllers.command.EventController import EventController
from app.models.user_model import User
from app.utils.pika import RabbitMQConnection


@get("/")
async def hello_world(request: Request[User, Token, Any]) -> str:
    # Publish the message to the 'hello' queue
    with RabbitMQConnection() as conn:
        conn.publish_message('hello', {'message': 'Hello from Controller!'})
    return f"Hello, user '{request.user}' with id '{request.auth.sub}'!"


# PostgreSQL connection string: postgresql+asyncpg://admin:admin@localhost:5432/db_name
# SQLite connection string: sqlite+aiosqlite:///test.sqlite
session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string="postgresql+asyncpg://admin:admin@localhost:5432/db_name",
    session_config=session_config,
)  # Create 'async_session' dependency.
sqlalchemy_plugin = SQLAlchemyInitPlugin(config=sqlalchemy_config)


async def on_startup(app: Litestar) -> None:
    """Initializes the database."""
    async with app.state.db_engine.begin() as conn:
        #await conn.run_sync(UUIDBase.metadata.drop_all) # <---- Uncomment this if you need to reset database
        await conn.run_sync(UUIDBase.metadata.create_all)


openapi_config = OpenAPIConfig(
    title="Command API",
    version="1.0.0",
)

app = Litestar(
    plugins=[SQLAlchemyInitPlugin(sqlalchemy_config)],
    on_startup=[on_startup],
    on_app_init=[jwt_auth.on_app_init],
    route_handlers=[
        hello_world,
        UserController,
        TagController,
        PostController,
        CommentController,
        EventController
    ],
    openapi_config=openapi_config,
)
