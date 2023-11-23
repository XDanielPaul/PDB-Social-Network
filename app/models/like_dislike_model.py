import json

from litestar.contrib.sqlalchemy.base import UUIDBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto import DTOConfig
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .post_model import posts_shared_association


class LikeDislike(UUIDBase):
    __tablename__ = 'like_dislike'
    review_type: Mapped[bool]

    reviewed_by_id = Column(ForeignKey('users.id'))
    reviewed_by = relationship("User", back_populates="likes_dislikes")

    reviewed_on_id = Column(ForeignKey('posts.id'))
    reviewed_on = relationship("Post", back_populates="likes_dislikes")

    def to_dict_create(self):
        return {
            '_id': str(self.reviewed_by_id) + '@' + str(self.reviewed_on_id),
            'reviewed_by_id': str(self.reviewed_by_id),
            'reviewed_on_id': str(self.reviewed_on_id),
            'type': self.review_type,
        }

    def to_dict_delete(self):
        return {
            '_id': str(self.reviewed_by_id) + '@' + str(self.reviewed_on_id),
        }

    def format_for_rabbit(self, method):
        message = {'model': self.__tablename__, 'method': method}
        match method:
            case 'CREATE':
                message['data'] = self.to_dict_create()
            case 'DELETE':
                message['data'] = self.to_dict_delete()
        return json.dumps(message)
