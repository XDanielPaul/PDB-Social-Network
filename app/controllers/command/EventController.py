from litestar.controller import Controller
from litestar import post,  Request
from app.models.event_model import Event, EventCreate, EventCreateDto, EventModel
from app.models.user_model import User
from litestar.dto import DTOData
from sqlalchemy.ext.asyncio import AsyncSession
from typing import  Any
from litestar.contrib.jwt import Token
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND
class EventController(Controller):
    path = "/event"

    @post('/',dto=EventCreateDto,tags=["Event"])
    async def create_event(
        self,
        data:  DTOData[EventCreate],
        request: Request[User, Token, Any],
        db_session: AsyncSession
    ) -> EventModel:
        data_dct = data.create_instance()
        db_user = await db_session.get(User, request.auth.sub)
        if not db_user:
            raise HTTPException(
                detail="User which submits the follow of the post doesnt exist.",
                status_code=HTTP_404_NOT_FOUND,
            )
        print(data_dct)
        