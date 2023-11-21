from typing import Annotated
from uuid import UUID

from litestar.contrib.pydantic import PydanticDTO
from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto import DTOConfig, DTOData
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

tags_posts_associations = Table(
    'tagged_posts',
    UUIDBase.metadata,
    Column('tag_name', ForeignKey('tags.id'), primary_key=True),
    Column('tag_post', ForeignKey('posts.id'), primary_key=True),
)


class Tag(UUIDBase):
    __tablename__ = 'tags'
    name: Mapped[str]

    tagged_posts = relationship('Post', secondary=tags_posts_associations, back_populates='tagged')

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

    def to_dict_create(self):
        return {'_id': str(self.id), 'name': self.name}
    def to_dict_delete(self):
        return {
            '_id': str(self.id)
        }
    def format_for_rabbit(self, method):
        message = {'model': self.__tablename__, 'method': method}
        match method:
            case 'ADD':
                return self.to_dict_create()


class TagPost(BaseModel):
    name: str


class PartialTagPostDTO(PydanticDTO[TagPost]):
    config = DTOConfig(partial=True)


class TagReturn(BaseModel):
    id: UUID
    name: str


class TagPostDTO(PydanticDTO[TagReturn]):
    config = DTOConfig(partial=True)
