from uuid import UUID

from litestar import Request, Response, delete, get, post, put
from litestar.connection import ASGIConnection
from litestar.contrib.jwt import JWTAuth, Token
from litestar.controller import Controller
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from app.utils.mongo.collections import *


class UserController(Controller):
    path = "/users"

    @get(path="/", tags=["User"])
    async def get_users(self) -> list[dict]:
        users = user_collection.find_documents({})
        return users

    @get(path="/{id:uuid}", tags=["User"])
    async def get_user(self, id: UUID) -> dict:
        user = user_collection.find_document({"_id": str(id)})
        if not user:
            raise HTTPException(detail="User does not exist", status_code=HTTP_404_NOT_FOUND)
        return user

    @get(path="/{id:uuid}/posts", tags=["User"])
    async def get_user_posts(self, id: UUID) -> dict:
        user = user_collection.find_document({"_id": str(id)})
        if not user:
            raise HTTPException(detail="User does not exist", status_code=HTTP_404_NOT_FOUND)
        posts = post_collection.find_documents({"created_by_id": str(id)})
        return posts

    @get(path="/{id:uuid}/followers", tags=["User"])
    async def get_user_followers(self, id: UUID) -> dict:
        user = user_collection.find_document({"_id": str(id)})
        if not user:
            raise HTTPException(detail="User does not exist", status_code=HTTP_404_NOT_FOUND)
        followers = user_collection.find_documents({"followers": str(id)})
        return followers

    @get(path="/{id:uuid}/following", tags=["User"])
    async def get_user_following(self, id: UUID) -> dict:
        user = user_collection.find_document({"_id": str(id)})
        if not user:
            raise HTTPException(detail="User does not exist", status_code=HTTP_404_NOT_FOUND)
        following = user_collection.find_documents({"following": str(id)})
        return following
