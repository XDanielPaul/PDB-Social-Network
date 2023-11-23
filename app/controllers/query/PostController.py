from uuid import UUID

from litestar import Request, Response, delete, get, post, put
from litestar.connection import ASGIConnection
from litestar.contrib.jwt import Token
from litestar.controller import Controller
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from app.utils.mongo.collections import *


def substitute_ids_for_objects(posts: list[dict]) -> list[dict]:
    for post in posts:
        post['comments'] = comment_collection.find_documents({'on_post_id': post['_id']})
        post['shared_by_users'] = user_collection.find_documents({'shared_posts': post['_id']})
        post['likes_dislikes'] = like_dislike_collection.find_documents(
            {'reviewed_on_id': post['_id']}
        )
        post['tags'] = tag_collection.find_documents({'_id': {'$in': post['tags']}})
    return posts


class PostController(Controller):
    path = '/posts'

    @get(path='/', tags=['Posts'])
    async def get_posts(self) -> list[dict]:
        posts = post_collection.find_documents({})
        return substitute_ids_for_objects(posts)

    @get(path='/{id:uuid}', tags=['Posts'])
    async def get_post(self, id: UUID) -> dict:
        post = post_collection.find_document({'_id': str(id)})
        if not post:
            raise HTTPException(detail='Post does not exist', status_code=HTTP_404_NOT_FOUND)
        return substitute_ids_for_objects(post)

    # Get posts containing a list of tags
    @get(path='/tags', tags=['Posts'])
    async def get_posts_by_tags(self, tags: list[str]) -> dict:
        tags = tag_collection.find_documents({'name': {'$in': tags}})
        tags_ids = [tag['_id'] for tag in tags]

        posts = post_collection.find_documents({'tags': {'$in': tags_ids}})
        return substitute_ids_for_objects(posts)

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
        return substitute_ids_for_objects(rated_posts)
