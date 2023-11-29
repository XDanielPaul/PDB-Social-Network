from typing import Any
from uuid import UUID

from litestar import Request, get
from litestar.contrib.jwt import Token
from litestar.controller import Controller
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND

from app.utils.mongo.collections import *
from app.utils.query import expand_ids_to_objects_event


class EventController(Controller):
    path = "/events"

    @get(path="/", tags=["Event"])
    async def get_events(self) -> list[dict]:
        events = event_collection.find_documents({})
        events = list(
            filter(
                lambda event: len(event.get("attending_users", []))
                < event.get("capacity", float('inf')),
                events,
            )
        )
        return expand_ids_to_objects_event(events)

    @get(path="/{id:uuid}", tags=["Event"])
    async def get_event(self, id: UUID) -> dict:
        event = event_collection.find_document({"_id": str(id)})
        if not event:
            raise HTTPException(detail="Event does not exist", status_code=HTTP_404_NOT_FOUND)
        return expand_ids_to_objects_event([event])

    @get(path="/my_events", tags=["Event"])
    async def get_my_events(self, request: Request[dict, Token, Any]) -> dict:
        events = event_collection.find_documents({"created_by_id": request.auth.sub})
        return expand_ids_to_objects_event(events)

    @get(path="/{id:uuid}/participants", tags=["Event"])
    async def get_event_participants(self, id: UUID) -> list[dict]:
        event = event_collection.find_document({"_id": str(id)})
        if not event:
            raise HTTPException(detail="Event does not exist", status_code=HTTP_404_NOT_FOUND)
        try:
            participants = user_collection.find_documents(
                {"_id": {"$in": event["attending_users"]}}
            )
            return participants
        except:
            return []

    @get(path="/my_attending", tags=["Event"])
    async def get_my_attending_events(self, request: Request[dict, Token, Any]) -> list[dict]:
        events = event_collection.find_documents({"attending_users": request.auth.sub})
        return expand_ids_to_objects_event(events)
