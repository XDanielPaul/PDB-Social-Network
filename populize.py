from app.models import (create_users,
    create_posts,
    create_comments,
    create_shared_posts,
    create_likes_dislikes,
    create_events,
    create_attending_users,
    create_follows
)
from app.models.user_model import User, user_followers_association
from app.models.comment_model import Comment
from app.models.event_model import Event, event_attending_associations
from app.models.like_dislike_model import LikeDislike
from app.models.post_model import Post, posts_shared_association
from app.models.tag_model import Tag, tags_posts_associations
from litestar.contrib.sqlalchemy.base import UUIDBase
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, selectinload
from faker import Faker

connection_string = "postgresql://admin:admin@localhost:5432/db_name"
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
fake = Faker()

if __name__ == "__main__":
    # Database reset
    UUIDBase.metadata.drop_all(engine)
    UUIDBase.metadata.create_all(engine)

    while True:
        question = input('What do you want? (Y for generating all data)')

        if question == "Y":
            print("Generating users...")
            generated_users = create_users()
            print("Generating follows")
            create_follows(generated_users)
            print("Generating posts...")
            posts = create_posts(generated_users)
            print("Generating comments...")
            create_comments(generated_users, posts)
            print("Generating shared posts...")
            create_shared_posts(generated_users, posts)
            print("Generating likes and dislikes...")
            create_likes_dislikes(generated_users, posts)
            print("Generating events...")
            events = create_events(generated_users)
            print("Generating attending users...")
            create_attending_users(generated_users, events)
            break
        else:
            print("Run again and press Y for god sage")
            break