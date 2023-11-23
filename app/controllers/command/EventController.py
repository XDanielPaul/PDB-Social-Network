from litestar.controller import Controller
from litestar import post, Request, delete
from app.models.event_model import Event, EventCreate, EventCreateDto, EventModel, AttendConfirm
from app.models.user_model import User
from litestar.dto import DTOData
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
from litestar.contrib.jwt import Token
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from app.utils.pika import RabbitMQConnection
from app.models.base_for_modelling import DeleteConfirm
from uuid import UUID


class EventController(Controller):
    path = "/event"

    @post('/', dto=EventCreateDto, tags=["Event"])
    async def create_event(
        self,
        data: DTOData[EventCreate],
        request: Request[User, Token, Any],
        db_session: AsyncSession,
    ) -> EventModel:
        data_dct = data.create_instance()
        db_user = await db_session.get(User, request.auth.sub)
        if not db_user:
            raise HTTPException(
                detail="User which submits the follow of the post doesnt exist.",
                status_code=HTTP_404_NOT_FOUND,
            )

        if data_dct.capacity < 2:
            raise HTTPException(
                detail="Capacity needs to be at  least 2.", status_code=HTTP_400_BAD_REQUEST
            )

        event_db = Event(created_event_id=db_user.id, event_pict="NULL", **(data_dct.model_dump()))

        try:
            db_session.add(event_db)
            await db_session.commit()
            await db_session.refresh(event_db)
        except Exception as err:
            print(err)
            raise HTTPException(detail=str(err), status_code=HTTP_400_BAD_REQUEST)
        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', event_db.format_for_rabbit('CREATE'))

        return_model = EventModel(
            id=event_db.id,
            name=event_db.name,
            description=event_db.description,
            capacity=event_db.capacity,
            event_datetime=event_db.event_datetime,
            event_pict=event_db.event_pict,
            created_event_id=event_db.created_event_id,
        )

        return return_model

    @delete('/{event_id:uuid}', status_code=200, tags=["Event"])
    async def delete_event(
        self,
        event_id: UUID,
        request: Request[User, Token, Any],
        db_session: AsyncSession,
    ) -> DeleteConfirm:
        db_event: Event = await db_session.get(Event, event_id)
        if not db_event:
            raise HTTPException(
                detail="Event with this ID doesn't exist.", status_code=HTTP_404_NOT_FOUND
            )
        if str(db_event.created_event_id) != request.auth.sub:
            raise HTTPException(
                detail="You can't delete this post", status_code=HTTP_401_UNAUTHORIZED
            )
        await db_session.delete(db_event)
        await db_session.commit()
        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', db_event.format_for_rabbit('DELETE'))

        return DeleteConfirm(deleted=True, message="Event was deleted.")

    @post('/attend/{event_id:uuid}', tags=["Event"])
    async def attend_event(
        self, event_id: UUID, request: Request[User, Token, Any], db_session: AsyncSession
    ) -> AttendConfirm:
        pass

    @post('/leave/{event_id:uuid}', tags=["Event"])
    async def leave_event(
        self, event_id: UUID, request: Request[User, Token, Any], db_session: AsyncSession
    ) -> AttendConfirm:
        pass
