import motor.motor_asyncio as motor
from litestar import Litestar, get
from litestar.openapi.config import OpenAPIConfig

from app.controllers.query.CommentController import CommentController
from app.controllers.query.EventController import EventController
from app.controllers.query.PostController import PostController
from app.controllers.query.TagController import TagController
from app.controllers.query.UserController import UserController, jwt_auth

local_connection_string = ""

client = motor.AsyncIOMotorClient("mongodb://admin:admin@127.0.0.1:27017/")
try:
    client.admin.command('ping')
    print("Pinged your deployment. You have successfully connected to MongoDB!")
except Exception as e:
    print(e)

mongo_db = client["social_db"]

openapi_config = OpenAPIConfig(
    title="Query API",
    version="1.0.0",
)

app = Litestar(
    route_handlers=[
        UserController,
        PostController,
        EventController,
        TagController,
        CommentController,
    ],
    on_app_init=[jwt_auth.on_app_init],
    openapi_config=openapi_config,
)
