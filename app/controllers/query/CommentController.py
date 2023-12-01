from uuid import UUID

from litestar import get
from litestar.controller import Controller
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND

from app.utils.mongo.collections import *


# Comment controller for read operations
class CommentController(Controller):
    path = "/comments"

    # Get all comments
    @get(path="/", tags=["Comment"])
    async def get_comments(self) -> list[dict]:
        comments = comment_collection.find_documents({})
        return comments

    # Get a comment by id
    @get(path="/{id:uuid}", tags=["Comment"])
    async def get_comment(self, id: UUID) -> dict:
        comment = comment_collection.find_document({"_id": str(id)})
        if not comment:
            raise HTTPException(detail="Comment does not exist", status_code=HTTP_404_NOT_FOUND)
        return comment

    # Get all comments on a post
    @get(path="/post_comments/{id:uuid}", tags=["Comment"])
    async def get_post_comments(self, id: UUID) -> list[dict]:
        comments = comment_collection.find_documents({"on_post_id": str(id)})
        return comments
