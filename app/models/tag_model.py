from typing import Annotated

from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto import DTOConfig
from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.utils.controller import Service

tags_posts_associations = Table(
    'tagged_posts', UUIDBase.metadata,
    Column('tag_name', ForeignKey('tags.id'), primary_key=True),
    Column('tag_post', ForeignKey('posts.id'), primary_key=True),
)


class Tag(UUIDBase):
    __tablename__ = 'tags'
    name: Mapped[str]

    tagged_posts = relationship(
        'Post', secondary=tags_posts_associations, back_populates='tagged')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }
