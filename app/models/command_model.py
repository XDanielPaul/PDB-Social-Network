import os
import sys
from datetime import date
from typing import Annotated

from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto import DTOConfig, Mark, dto_field
from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ..utils.controller import Service


# UUIDBase includes UUID based primary key (id)
class UserModel(UUIDBase):
    __tablename__ = 'users'
    username: Mapped[str]
    password: Mapped[str]

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


class Service(Service[UserModel]):
    repository_type = UserRepository


write_config = DTOConfig()  # Create a DTOConfig instance for write operations
WriteDTO = SQLAlchemyDTO[Annotated[UserModel, write_config]]
ReadDTO = SQLAlchemyDTO[UserModel]


# UUIDAuditBase includes UUID based primary key (id), created_at, updated_at
class Post(UUIDAuditBase):
    __tablename__ = 'posts'
    title: Mapped[str]
    content: Mapped[str]
