
from typing import Annotated

from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto import DTOConfig
from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.utils.controller import Service
from .post_model import posts_shared_association


class LikeDislike(UUIDBase):
    review_type: Mapped[bool]

    reviewed_by_id = Column(ForeignKey('users.id'))
    reviewed_by = relationship("UserModel", back_populates="likes_dislikes")

    reviewed_on_id = Column(ForeignKey('posts.id'))
    reviewed_on = relationship("Post", back_populates="likes_dislikes")
