import asyncio
import json
from typing import Any
from uuid import UUID

from litestar import Request, delete, post
from litestar.contrib.jwt import Token
from litestar.controller import Controller
from litestar.dto import DTOData
from litestar.exceptions import HTTPException
from litestar.status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.base_for_modelling import DeleteConfirm
from app.models.event_model import (
    AttendConfirm,
    Event,
    EventCreate,
    EventCreateDto,
    EventModel,
    event_attending_associations,
)
from app.models.user_model import User
from app.utils.pika import RabbitMQConnection


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
        user_db = await db_session.get(User, request.auth.sub)
        if not user_db:
            raise HTTPException(
                detail="User submitting the request doesn't exist", status_code=HTTP_404_NOT_FOUND
            )
        # check if event exist
        request_db = await db_session.execute(
            select(Event).filter(Event.id == event_id).options(selectinload(Event.attending_users))
        )
        event_db = request_db.scalars().first()
        if not event_db:
            raise HTTPException(detail="Event doesn't exist.", status_code=HTTP_404_NOT_FOUND)
        # check if user is not already in the event

        check_user = user_db.id in [event_user.id for event_user in event_db.attending_users]
        if check_user:
            raise HTTPException(
                detail="User is already registered to this event.", status_code=HTTP_409_CONFLICT
            )

        if (len(event_db.attending_users) + 1) > event_db.capacity:
            raise HTTPException(
                detail="There is no space for you in this event.", status_code=HTTP_409_CONFLICT
            )

        try:
            with RabbitMQConnection() as conn:
                conn.publish_message_with_ack(
                    'events',
                    json.dumps(
                        {
                            'method': 'REGISTER',
                            'user_id': str(user_db.id),
                            'event_id': str(event_db.id),
                            'model': 'events',
                        }
                    ),
                )
            result = await db_session.execute(
                select(Event).filter(Event.id == event_id, Event.updated_at == event_db.updated_at)
            )

            result_db = result.scalars().first()
            if result_db:
                db_request = event_attending_associations.insert().values(
                    {'user_attending': user_db.id, 'on_event': event_db.id}
                )
                print(db_request)
                await db_session.execute(db_request)
                await db_session.commit()
            else:
                raise HTTPException(
                    detail="There was a conflict in the registering", status_code=HTTP_409_CONFLICT
                )
        except HTTPException as exception:
            raise exception
        except Exception as err:
            print("#" * 50, "\n", err, "\n", "#" * 50)
            raise HTTPException(
                detail="Something went wrong when registering to event.",
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return AttendConfirm(
            event_id=event_id,
            current_capacity_left=(event_db.capacity - (len(event_db.attending_users) + 1)),
            result=True,
        )

    @post('/leave/{event_id:uuid}', tags=["Event"])
    async def leave_event(
        self, event_id: UUID, request: Request[User, Token, Any], db_session: AsyncSession
    ) -> AttendConfirm:
        user_db = await db_session.get(User, request.auth.sub)
        if not user_db:
            raise HTTPException(
                detail="User submitting the request doesn't exist", status_code=HTTP_404_NOT_FOUND
            )
        db_request = await db_session.execute(
            select(Event).filter(Event.id == event_id).options(selectinload(Event.attending_users))
        )
        event_db: Event = db_request.scalars().first()
        if not event_db:
            raise HTTPException(detail="Event doesn't exist.", status_code=HTTP_404_NOT_FOUND)

        event_db.attending_users.remove(user_db)
        await db_session.commit()

        with RabbitMQConnection() as conn:
            conn.publish_message(
                'events',
                json.dumps(
                    {
                        'method': 'LEAVE',
                        'model': 'events',
                        'user_id': str(user_db.id),
                        'event_id': str(event_id),
                    }
                ),
            )

        return AttendConfirm(
            event_id=event_id,
            current_capacity_left=event_db.capacity - len(event_db.attending_users),
            result=True,
        )
