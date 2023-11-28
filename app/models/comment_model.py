import json

from litestar.contrib.pydantic import PydanticDTO
from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from litestar.dto import DTOConfig
from pydantic import UUID4, BaseModel
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import Mapped, relationship

from .post_model import posts_shared_association


class Comment(UUIDAuditBase):
    __tablename__ = 'comments'
    content: Mapped[str]

    created_by_id = Column(ForeignKey("users.id"))
    created_comment_by = relationship("User", back_populates="comments", lazy='joined')

    on_post_id = Column(ForeignKey("posts.id"))
    on_post = relationship("Post", back_populates="comments", lazy='joined')

    def to_dict_create(self):
        return {
            '_id': str(self.id),
            'content': self.content,
            'created_by_id': str(self.created_by_id),
            'on_post_id': str(self.on_post_id),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    def to_dict_update(self):
        return {
            '_id': str(self.id),
            'content': self.content,
            'updated_at': self.updated_at,
        }

    def to_dict_delete(self):
        return {
            '_id': str(self.id),
        }

    def format_for_rabbit(self, method):
        message = {'model': self.__tablename__, 'method': method}
        match method:
            case 'CREATE':
                message['data'] = self.to_dict_create()
            case 'UPDATE':
                message['data'] = self.to_dict_update()
            case 'DELETE':
                message['data'] = self.to_dict_delete()
        return json.dumps(message,default=str)


class CommentCreate(BaseModel):
    content: str
    on_post_id: UUID4


class PartialCommentDto(PydanticDTO[CommentCreate]):
    config = DTOConfig(partial=True)


class UpdateComment(BaseModel):
    id: UUID4
    content: str


class PartialUpdateCommentDto(PydanticDTO[UpdateComment]):
    config = DTOConfig(partial=True)
