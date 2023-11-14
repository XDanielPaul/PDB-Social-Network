
from typing import Annotated
from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto import DTOConfig
from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.utils.controller import Service
from .post_model import posts_shared_association


class Comment(UUIDAuditBase):
    __tablename__ = 'comments'
    content: Mapped[str]

    created_by_id = Column(ForeignKey("users.id"))
    created_comment_by = relationship("UserModel", back_populates="comments")

    on_post_id = Column(ForeignKey("posts.id"))
    on_post = relationship("Post", back_populates="comments")
