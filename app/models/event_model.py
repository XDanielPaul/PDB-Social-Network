import json
from datetime import datetime
from uuid import UUID

from litestar.contrib.pydantic import PydanticDTO
from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.dto import DTOConfig
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, relationship

event_attending_associations = Table(
    'event_attending',
    UUIDBase.metadata,
    Column('user_attending', ForeignKey('users.id'), primary_key=True),
    Column('on_event', ForeignKey('events.id'), primary_key=True),
)


# Event model for command
class Event(UUIDAuditBase):
    __tablename__ = 'events'

    name: Mapped[str]
    description: Mapped[str]
    event_pict: Mapped[str]
    capacity: Mapped[int]
    event_datetime: Mapped[datetime]
    created_event_id = Column(ForeignKey('users.id'))
    created_event = relationship('User', back_populates='created_events')

    attending_users = relationship(
        'User',
        secondary=event_attending_associations,
        back_populates='attending_events',
    )

    def to_dict_create(self):
        return {
            '_id': str(self.id),
            'name': self.name,
            'description': self.description,
            'event_pict': self.event_pict,
            'capacity': self.capacity,
            'event_datetime': self.event_datetime,
            'created_event_id': str(self.created_event_id),
        }

    def to_dict_delete(self):
        return {'_id': str(self.id)}

    def format_for_rabbit(self, method):
        message = {'model': self.__tablename__, 'method': method}
        match method:
            case 'CREATE':
                message['data'] = self.to_dict_create()
            case 'DELETE':
                message['data'] = self.to_dict_delete()

        return json.dumps(message, default=str)


class EventCreate(BaseModel):
    name: str
    description: str
    capacity: int
    event_datetime: datetime


class EventCreateDto(PydanticDTO[EventCreate]):
    config = DTOConfig(partial=True)


class EventModel(EventCreate):
    id: UUID
    event_pict: str
    created_event_id: UUID


class AttendConfirm(BaseModel):
    event_id: UUID
    current_capacity_left: int
    result: bool
