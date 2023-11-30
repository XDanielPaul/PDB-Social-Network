from uuid import UUID

from litestar import get
from litestar.controller import Controller
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND

from app.utils.mongo.collections import *


class TagController(Controller):
    path = "/tags"

    @get(path="/", tags=["Tag"])
    async def get_tags(self) -> list[dict]:
        tags = tag_collection.find_documents({})
        return tags

    @get(path="/{id:uuid}", tags=["Tag"])
    async def get_tag(self, id: UUID) -> dict:
        tag = tag_collection.find_document({"_id": str(id)})
        if not tag:
            raise HTTPException(detail="Tag does not exist", status_code=HTTP_404_NOT_FOUND)
        return tag
