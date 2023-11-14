import os
import sys
from datetime import date
from typing import Annotated

from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto import DTOConfig, Mark, dto_field
from sqlalchemy import ForeignKey, select, Table, Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from app.utils.controller import Service

user_followers_association = Table(
    'user_followers', UUIDBase.metadata,
    Column('follower_id',ForeignKey('users.id'),primary_key=True),
    Column('followed_id',ForeignKey('users.id'),primary_key=True),
)

# UUIDBase includes UUID based primary key (id)
class UserModel(UUIDBase):
    __tablename__ = 'users'
    username: Mapped[str]
    password: Mapped[str]
    profile_picture: Mapped[str]
    profile_bio: Mapped[str]


    followers = relationship(
        'UserModel',
        secondary=user_followers_association,
        primaryjoin="UserModel.id == user_followers.c.followed_id",
        secondaryjoin="UserModel.id == user_followers.c.follower_id",
        backref="followed_by",
        lazy="dynamic"
    )
    following = relationship(
        'UserModel',
        secondary=user_followers_association,
        primaryjoin="UserModel.id == user_followers.c.follower_id",
        secondaryjoin="UserModel.id == user_followers.c.followed_id",
    )

    def to_dict(user_instance, method):
        return {
            'method': method,
            'class': user_instance.__class__.__name__,
            'username': user_instance.username,
            'password': user_instance.password,
        }

    def __repr__(self):
        # Do not print password?
        return f"<UserModel: id='{self.id}', username='{self.username}' >"


class UserRepository(SQLAlchemyAsyncRepository[UserModel]):
    """User repository"""

    model_type = UserModel


class UserService(Service[UserModel]):
    repository_type = UserRepository


write_config = DTOConfig()  # Create a DTOConfig instance for write operations
WriteDTO = SQLAlchemyDTO[Annotated[UserModel, write_config]]
ReadDTO = SQLAlchemyDTO[UserModel]
