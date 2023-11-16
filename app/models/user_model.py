
from typing import Annotated
from uuid import UUID
from litestar.contrib.sqlalchemy.base import UUIDAuditBase, UUIDBase
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from litestar.dto import DTOConfig
from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.utils.controller import Service
from .post_model import posts_shared_association
from .event_model import event_attending_associations
from .base_for_modelling import BaseModel
from litestar.dto import DTOConfig, DTOData
from litestar.contrib.pydantic import PydanticDTO

user_followers_association = Table(
    'user_followers', UUIDBase.metadata,
    Column('follower_id', ForeignKey('users.id'), primary_key=True),
    Column('followed_id', ForeignKey('users.id'), primary_key=True),
)


class UserModel(UUIDBase):
    __tablename__ = 'users'
    username: Mapped[str]
    password: Mapped[str]
    profile_picture: Mapped[str]
    profile_bio: Mapped[str]

    followers = relationship(
        'UserModel',
        secondary=user_followers_association,
        primaryjoin="UserModel.id == user_followers.c.followed_id",
        secondaryjoin="UserModel.id == user_followers.c.follower_id",
        back_populates='following'
    )
    following = relationship(
        'UserModel',
        secondary=user_followers_association,
        primaryjoin="UserModel.id == user_followers.c.follower_id",
        secondaryjoin="UserModel.id == user_followers.c.followed_id",
        back_populates='followers'
    )
    posts = relationship("Post", back_populates="created_by")

    shared_posts = relationship(
        'Post', secondary=posts_shared_association, back_populates='shared_by_users')
    comments = relationship('Comment', back_populates="created_comment_by")
    likes_dislikes = relationship('LikeDislike', back_populates="reviewed_by")
    created_events = relationship('Event', back_populates='created_event')
    attending_events = relationship(
        'Event', secondary=event_attending_associations, back_populates='attending_users')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'profile_picture': self.profile_picture,
            'profile_bio': self.profile_bio
        }

    def __repr__(self):
        # Do not print password?
        return f"<UserModel: id='{self.id}', username='{self.username}' >"


class UserRepository(SQLAlchemyAsyncRepository[UserModel]):
    """User repository"""

    model_type = UserModel


class UserService(Service[UserModel]):
    repository_type = UserRepository


write_config = DTOConfig()  # Create a DTOConfig instance for write operations
WriteDTO = SQLAlchemyDTO[Annotated[UserModel, write_config]]
ReadDTO = SQLAlchemyDTO[UserModel]


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
