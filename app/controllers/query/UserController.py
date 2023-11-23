from typing import Any, Optional
from uuid import UUID

from litestar import Request, get
from litestar.connection import ASGIConnection
from litestar.contrib.jwt import JWTAuth, Token
from litestar.controller import Controller
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND

from app.utils.mongo.collections import *
from app.utils.query import expand_ids_to_objects_post, expand_ids_to_objects_user


# Authentication
async def retrieve_user_handler(
    token: Token, connection: ASGIConnection[Any, Any, Any, Any]
) -> Optional[dict]:
    user = user_collection.find_document({"_id": token.sub})

    if not user:
        return None
    return user


jwt_auth = JWTAuth[dict](
    retrieve_user_handler=retrieve_user_handler,
    token_secret="secret",
    exclude=['/schema'],
)


class UserController(Controller):
    path = "/users"

    @get(path="/", tags=["User"])
    async def get_users(self) -> list[dict]:
        users = user_collection.find_documents({})
        return expand_ids_to_objects_user(users)

    @get(path="/{id:uuid}", tags=["User"])
    async def get_user(self, id: UUID) -> dict:
        user = user_collection.find_document({"_id": str(id)})
        if not user:
            raise HTTPException(detail="User does not exist", status_code=HTTP_404_NOT_FOUND)
        return expand_ids_to_objects_user(user)

    @get(path="/{id:uuid}/posts", tags=["User"])
    async def get_user_posts(self, id: UUID) -> dict:
        user = user_collection.find_document({"_id": str(id)})
        if not user:
            raise HTTPException(detail="User does not exist", status_code=HTTP_404_NOT_FOUND)
        posts = post_collection.find_documents({"created_by_id": str(id)})
        return expand_ids_to_objects_post(posts)

    @get(path="/{id:uuid}/followers", tags=["User"])
    async def get_user_followers(self, id: UUID) -> dict:
        user = user_collection.find_document({"_id": str(id)})
        if not user:
            raise HTTPException(detail="User does not exist", status_code=HTTP_404_NOT_FOUND)
        followers = user_collection.find_documents({"followers": str(id)})
        return expand_ids_to_objects_user(followers)

    @get(path="/{id:uuid}/following", tags=["User"])
    async def get_user_following(self, id: UUID) -> dict:
        user = user_collection.find_document({"_id": str(id)})
        if not user:
            raise HTTPException(detail="User does not exist", status_code=HTTP_404_NOT_FOUND)
        following = user_collection.find_documents({"following": str(id)})
        return expand_ids_to_objects_user(following)

    @get(path="/my_followers", tags=["User"])
    async def get_my_followers(self, request: Request[dict, Token, Any]) -> dict:
        followers = user_collection.find_documents({"followers": request.auth.sub})
        return followers

    @get(path="/my_following", tags=["User"])
    async def get_my_following(self, request: Request[dict, Token, Any]) -> dict:
        following = user_collection.find_documents({"following": request.auth.sub})
        return following
