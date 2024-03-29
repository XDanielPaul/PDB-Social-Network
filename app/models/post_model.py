import json

from litestar.contrib.pydantic import PydanticDTO
from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.dto import DTOConfig
from pydantic import UUID4, BaseModel
from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .tag_model import tags_posts_associations

posts_shared_association = Table(
    'posts_shared',
    UUIDBase.metadata,
    Column('shared_by', ForeignKey('users.id'), primary_key=True),
    Column('shared_post', ForeignKey('posts.id'), primary_key=True),
)


# Post model for command
class Post(UUIDAuditBase):
    __tablename__ = 'posts'
    title: Mapped[str] = mapped_column(String(1024))
    content: Mapped[str]
    image_ref: Mapped[str] = mapped_column(String, default="DOESNT/EXIST/42")

    created_by_id = Column(ForeignKey("users.id"))
    created_by = relationship("User", back_populates="posts")

    shared_by_users = relationship(
        'User', secondary=posts_shared_association, back_populates='shared_posts', lazy='joined'
    )
    comments = relationship('Comment', back_populates="on_post", lazy='joined')

    likes_dislikes = relationship('LikeDislike', back_populates="reviewed_on")

    tagged = relationship('Tag', secondary=tags_posts_associations, back_populates='tagged_posts')

    def to_dict_create(self):
        return {
            '_id': str(self.id),
            'title': self.title,
            'content': self.content,
            'created_by_id': str(self.created_by_id),
            'image_ref': self.image_ref,
            'comments': [],
            'shared_by_users': [],
            'tags': [],
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    def to_dict_delete(self):
        return {'_id': str(self.id)}

    def format_for_rabbit(self, method):
        message = {'model': self.__tablename__, 'method': method}
        match method:
            case 'CREATE':
                message['data'] = self.to_dict_create()
            case 'DELETE':
                message['data'] = self.to_dict_delete()

        return json.dumps(message, default=str)


class TagInPost(BaseModel):
    name: str


class PostCreate(BaseModel):
    title: str
    content: str
    tags: list[TagInPost]


class PartialPostDto(PydanticDTO[PostCreate]):
    config = DTOConfig(partial=True)


class PostReturnModel(PostCreate):
    id: UUID4

    class Config:
        exclude = ['tags']


class PartialPostReturnDto(PydanticDTO[PostReturnModel]):
    config = DTOConfig(partial=True)


class PostLikeDislike(BaseModel):
    post_id: UUID4
    like: bool


class PostLikeDislikeDto(PydanticDTO[PostLikeDislike]):
    config = DTOConfig(partial=True)


class LikeDislikeModel(BaseModel):
    user_id: UUID4
    post_id: UUID4
    review_type: bool


class LikeDislikeDeleteModel(BaseModel):
    post_id: str


class LikeDislikeDeleteModelDto(PydanticDTO[LikeDislikeDeleteModel]):
    config = DTOConfig(partial=True)
