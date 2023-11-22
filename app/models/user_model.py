import json
from typing import Annotated
from uuid import UUID

from litestar.contrib.pydantic import PydanticDTO
from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto import DTOConfig, DTOData
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_for_modelling import BaseModel
from .event_model import event_attending_associations
from .post_model import posts_shared_association

user_followers_association = Table(
    'user_followers',
    UUIDBase.metadata,
    Column('follower_id', ForeignKey('users.id'), primary_key=True),
    Column('followed_id', ForeignKey('users.id'), primary_key=True),
)


class User(UUIDBase):
    __tablename__ = 'users'
    username: Mapped[str]
    password: Mapped[str]
    profile_picture: Mapped[str]
    profile_bio: Mapped[str]

    followers = relationship(
        'User',
        secondary=user_followers_association,
        primaryjoin="User.id == user_followers.c.followed_id",
        secondaryjoin="User.id == user_followers.c.follower_id",
        back_populates='following',
    )
    following = relationship(
        'User',
        secondary=user_followers_association,
        primaryjoin="User.id == user_followers.c.follower_id",
        secondaryjoin="User.id == user_followers.c.followed_id",
        back_populates='followers',
    )
    posts = relationship("Post", back_populates="created_by")

    shared_posts = relationship(
        'Post',
        secondary=posts_shared_association,
        back_populates='shared_by_users',
    )
    comments = relationship('Comment', back_populates="created_comment_by")
    likes_dislikes = relationship('LikeDislike', back_populates="reviewed_by")
    created_events = relationship('Event', back_populates='created_event')
    attending_events = relationship(
        'Event', secondary=event_attending_associations, back_populates='attending_users'
    )

    def to_dict_create(self):
        return {
            '_id': str(self.id),
            'username': self.username,
            'password': self.password,
            'profile_picture': self.profile_picture,
            'profile_bio': self.profile_bio,
            'postInfoIds': [],
            'followers': [],
            'follows': [],
            'shared_posts': [],
            'attending_events': [],
        }

    def to_dict_update(self):
        return {
            '_id': str(self.id),
            'username': self.username,
            'password': self.password,
            'profile_picture': self.profile_picture,
            'profile_bio': self.profile_bio,
        }

    def to_dict_delete(self):
        return {'_id': str(self.id)}

    def format_for_rabbit(self, method):
        message = {'model': self.__tablename__, 'method': method}

        match method:
            case 'CREATE':
                message['data'] = self.to_dict_create()
            case 'UPDATE':
                message['data'] = self.to_dict_update()
            case 'DELETE':
                message['data'] = self.to_dict_delete()

        return json.dumps(message)

    def __repr__(self):
        # Do not print password?
        return f"<User: id='{self.id}', username='{self.username}' >"


# class UserRepository(SQLAlchemyAsyncRepository[User]):
#    """User repository"""
#


# class UserService(Service[User]):


write_config = DTOConfig()  # Create a DTOConfig instance for write operations
WriteDTO = SQLAlchemyDTO[Annotated[User, write_config]]
ReadDTO = SQLAlchemyDTO[User]


class UserCreateModel(BaseModel):
    username: str
    password: str
    profile_picture: str
    profile_bio: str


class PartialUserDto(PydanticDTO[UserCreateModel]):
    config = DTOConfig(partial=True)


class UserReturn(UserCreateModel):
    id: UUID


class UserReturnDto(PydanticDTO[UserReturn]):
    config = DTOConfig(partial=True)


class UserLogin(BaseModel):
    username: str
    password: str


class PartiaUserLoginDto(PydanticDTO[UserLogin]):
    config = DTOConfig(partial=True)
