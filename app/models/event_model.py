from typing import Annotated
<<<<<<< HEAD
from uuid import UUID
from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
=======

from litestar.contrib.sqlalchemy.base import UUIDBase
>>>>>>> main
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.dto import DTOConfig
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from litestar.contrib.pydantic import PydanticDTO
from pydantic import BaseModel
from datetime import datetime

event_attending_associations = Table(
    'event_attending',
    UUIDBase.metadata,
    Column('user_attending', ForeignKey('users.id'), primary_key=True),
    Column('on_event', ForeignKey('events.id'), primary_key=True),
)


class Event(UUIDBase):
    __tablename__ = 'events'

    name: Mapped[str]
    description: Mapped[str]
    event_pict: Mapped[str]
    capacity: Mapped[int]
    event_datetime: Mapped[datetime]
    created_event_id = Column(ForeignKey('users.id'))
    created_event = relationship('User', back_populates='created_events')

    attending_users = relationship(
        'User', secondary=event_attending_associations, back_populates='attending_events'
    )


class EventCreate(BaseModel):
    title: str
    description: str
    capacity: int
    event_datetime: datetime



class EventCreateDto(PydanticDTO[EventCreate]):
    config = DTOConfig(partial=True)


class EventModel(EventCreate):
    id: UUID
    event_pict: str
