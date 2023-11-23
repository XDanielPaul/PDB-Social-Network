from typing import Any
from uuid import UUID

from litestar import Request
from litestar.contrib.jwt import Token
from litestar.controller import Controller
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND

from app.utils.mongo.collections import *
from app.utils.query import expand_ids_to_objects_post


class PostController(Controller):
    path = '/posts'

    @get(path='/', tags=['Posts'])
    async def get_posts(self) -> list[dict]:
        posts = post_collection.find_documents({})
        return expand_ids_to_objects_post(posts)

    @get(path='/{id:uuid}', tags=['Posts'])
    async def get_post(self, id: UUID) -> dict:
        post = post_collection.find_document({'_id': str(id)})
        if not post:
            raise HTTPException(detail='Post does not exist', status_code=HTTP_404_NOT_FOUND)
        return expand_ids_to_objects_post(post)

    # Get posts containing a list of tags
    @get(path='/tags', tags=['Posts'])
    async def get_posts_by_tags(self, tags: list[str]) -> dict:
        tags = tag_collection.find_documents({'name': {'$in': tags}})
        tags_ids = [tag['_id'] for tag in tags]

        posts = post_collection.find_documents({'tags': {'$in': tags_ids}})
        return expand_ids_to_objects_post(posts)

    # Filter posts by likes and dislikes count, likes ascending then dislikes descending
    @get(path='/rate_filter', tags=['Posts'])
    async def get_posts_by_likes_dislikes(self) -> dict:
        # Find posts in the database
        posts = post_collection.find_documents({})
        # Get the number of likes and dislikes for each post
        ratings = like_dislike_collection.find_documents({})
        # Sort posts by likes and dislikes count
        rated_posts = sorted(
            posts,
            key=lambda post: (
                ratings.count({'reviewed_on_id': post['_id'], 'rating': True}),
                ratings.count({'reviewed_on_id': post['_id'], 'rating': False}),
            ),
        )
        return expand_ids_to_objects_post(rated_posts)

    @get(path="/my_posts", tags=["Posts"])
    async def get_my_posts(self, request: Request[dict, Token, Any]) -> dict:
        posts = post_collection.find_documents({"created_by_id": request.auth.sub})
        return expand_ids_to_objects_post(posts)

    @get(path="/my_feed", tags=["Posts"])
    async def get_my_feed(self, request: Request[dict, Token, Any]) -> dict:
        follower_ids = user_collection.find_documents({"followers": request.auth.sub})
        posts_posted_by_followers = post_collection.find_documents(
            {"created_by_id": {"$in": follower_ids}}
        )
        ratings = like_dislike_collection.find_documents({})
        # Filter by likes and dislikes
        # TODO: Filter by created_at
        rated_posts = sorted(
            posts_posted_by_followers,
            key=lambda post: (
                ratings.count({'reviewed_on_id': post['_id'], 'rating': True}),
                ratings.count({'reviewed_on_id': post['_id'], 'rating': False}),
            ),
        )
        return expand_ids_to_objects_post(rated_posts)
