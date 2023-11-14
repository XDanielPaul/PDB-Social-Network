import os
import sys
from datetime import date
from typing import Annotated

from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto import DTOConfig, Mark, dto_field
from sqlalchemy import ForeignKey, select,  String, Column, Table
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from app.utils.controller import Service
from .tag_model import tags_posts_associations
posts_shared_association = Table(
    'posts_shared', UUIDBase.metadata,
    Column('shared_by', ForeignKey('users.id'), primary_key=True),
    Column('shared_post', ForeignKey('posts.id'), primary_key=True),
)


class Post(UUIDAuditBase):
    __tablename__ = 'posts'
    title: Mapped[str] = mapped_column(String(1024))
    content: Mapped[str]
    image_ref: Mapped[str]

    created_by_id = Column(ForeignKey("users.id"))
    created_by = relationship("UserModel", back_populates="posts")

    shared_by_users = relationship(
        'UserModel', secondary=posts_shared_association, back_populates='shared_posts')
    comments = relationship('Comment', back_populates="on_post")

    likes_dislikes = relationship('LikeDislike', back_populates="reviewed_on")

    tagged = relationship(
        'Tag', secondary=tags_posts_associations, back_populates='tagged_posts')
