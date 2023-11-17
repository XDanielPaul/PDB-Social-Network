from litestar import Litestar, get
from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.contrib.sqlalchemy.plugins.init import SQLAlchemyInitPlugin
from litestar.contrib.sqlalchemy.plugins.init.config import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
)

from app.controllers.command.TagController import TagController
from app.controllers.command.UserController import UserController
from app.controllers.command.PostController import PostController
from app.models.comment_model import Comment
from app.models.event_model import Event
from app.models.like_dislike_model import LikeDislike
from app.models.post_model import Post
from app.models.tag_model import Tag
from app.models.user_model import User
from app.utils.pika import RabbitMQConnection


@get("/")
async def hello_world() -> str:
    # Publish the message to the 'hello' queue
    with RabbitMQConnection() as conn:
        conn.publish_message('hello', {'message': 'Hello from Controller!'})
    return "Hello, Controller!"


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
        # await conn.run_sync(UUIDBase.metadata.drop_all) # <---- Uncomment this if you need to reset database
        await conn.run_sync(UUIDBase.metadata.create_all)


app = Litestar(
    plugins=[SQLAlchemyInitPlugin(sqlalchemy_config)],
    on_startup=[on_startup],
    route_handlers=[hello_world, UserController, TagController,PostController],
)
