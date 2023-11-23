from typing import Annotated

from litestar.contrib.sqlalchemy.base import UUIDBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto import DTOConfig
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    created_event_id = Column(ForeignKey('users.id'))
    created_event = relationship('User', back_populates='created_events')

    attending_users = relationship(
        'User', secondary=event_attending_associations, back_populates='attending_events'
    )
