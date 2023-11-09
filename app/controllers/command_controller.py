from litestar import Litestar, get
from litestar.contrib.sqlalchemy.base import UUIDBase
from litestar.contrib.sqlalchemy.plugins.init import SQLAlchemyInitPlugin
from litestar.contrib.sqlalchemy.plugins.init.config import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
)

from app.utils.pika import RabbitMQConnection
from app.controllers.command.UserController import UserController

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


async def on_startup() -> None:
    """Initializes the database."""
    async with sqlalchemy_config.get_engine().begin() as conn:
        await conn.run_sync(UUIDBase.metadata.create_all)


app = Litestar(
    route_handlers=[hello_world, UserController],
    on_startup=[on_startup],
    plugins=[SQLAlchemyInitPlugin(config=sqlalchemy_config)],
)
