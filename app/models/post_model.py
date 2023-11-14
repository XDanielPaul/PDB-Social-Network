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
from app.utils.controller import Service

# UUIDAuditBase includes UUID based primary key (id), created_at, updated_at
class Post(UUIDAuditBase):
    __tablename__ = 'posts'
    title: Mapped[str]
    content: Mapped[str]