from .user_model import User, user_followers_association
from .comment_model import Comment
from .event_model import Event, event_attending_associations
from .like_dislike_model import LikeDislike
from .post_model import Post, posts_shared_association
from .tag_model import Tag, tags_posts_associations
from litestar.contrib.sqlalchemy.base import UUIDBase
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, selectinload
import json
import sys
import random
from faker import Faker
import datetime
from datetime import timedelta
import pytz

# TODO
# [DONE] Create users
# [DONE] Create posts and tags
# [DONE] Create some shared posts
# [DONE] Create some comments
# [DONE] Create some likes and dislikes
# [DONE] Create some events
# [DONE] Create some attending users to events

from app.utils.pika import RabbitMQConnection

connection_string = "postgresql://admin:admin@localhost:5432/db_name"
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
fake = Faker()


def create_users():
    session = Session()
    path_to_file = './app/models/example_data/users.json'
    with open(path_to_file, 'r') as json_file:
        user_data = json.load(json_file)
    user_data = user_data['users']
    created_users: list[User] = []
    for user in user_data:
        user = User(**user)
        session.add(user)
        session.commit()
        session.refresh(user)
        created_users.append(user)

    for user in created_users:
        formated_data = user.format_for_rabbit('CREATE')
        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', formated_data)
    session.close()
    return created_users


def create_posts(users: list[User]):
    session = Session()
    Faker.seed(0)

    def generate_tag():
        return Tag(name=fake.word())

    def generate_post():
        return Post(
            title=fake.sentence(),
            content=fake.paragraph(nb_sentences=10),
            image_ref=f"/path/to/{fake.word()}.jpg",
            created_by_id=random.choice(users).id,
        )

    # adding tags to the database
    tags = [generate_tag() for _ in range(10)]
    session.add_all(tags)
    session.commit()
    for tag in tags:
        session.refresh(tag)
    # adding posts to the database
    posts = [generate_post() for _ in range(10)]
    session.add_all(posts)
    session.commit()

    for post in posts:
        session.refresh(post)

    tags_and_posts = {f"{post.id}": [] for post in posts}

    # adding tags to posts in Postgre
    for post in posts:
        for tag in random.sample(tags, k=3):
            tags_and_posts[f"{post.id}"].append(tag)
            insert_statement = tags_posts_associations.insert().values(
                {'tag_name': tag.id, 'tag_post': post.id}
            )
            session.execute(insert_statement)
    session.commit()
    # adding post and its tags to the mongo
    for post in posts:
        formated_data = post.format_for_rabbit('CREATE')
        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', formated_data)
            
    for post in posts:
        tags={
            'post_id': str(post.id),
            'tags': [tag.format_for_rabbit('ADD') for tag in tags_and_posts[f"{post.id}"]],
            'method': 'ADD',
        }
        with RabbitMQConnection() as conn:
            conn.publish_message('tags', json.dumps(tags))

    session.close()
    return posts


def create_comments(users: list[User], posts: list[Post]):
    sesion = Session()
    Faker.seed(0)
    formated_comments_rabbit = []
    comment_objects = []
    for user in users:
        posts_random = random.sample(posts, k=3)
        for post in posts_random:
            new_comment = Comment(
                content=fake.sentence(), created_by_id=user.id, on_post_id=post.id
            )
            # adding comment to database
            sesion.add(new_comment)
            sesion.commit()
            sesion.refresh(new_comment)
            # generating data for mongo connection
            formated_comments_rabbit.append(
                {'post_id': str(post.id), 'comment_id': str(new_comment.id), 'method': 'ADD'}
            )
            # need this for publishing comment to crud_operations
            comment_objects.append(new_comment)

    with RabbitMQConnection() as conn:
        # publishing comments
        for comment in comment_objects:
            conn.publish_message('crud_operations', comment.format_for_rabbit('CREATE'))
        # publishing relationships to mongo
        for formated_comment in formated_comments_rabbit:
            conn.publish_message('comments', json.dumps(formated_comment))

    sesion.close()


def create_shared_posts(users: list[User], posts: list[Post]):
    session = Session()
    shared_posts_all = []
    for user in users:
        shared_posts = random.sample(posts, k=2)
        for post in shared_posts:
            new_share = {'shared_post': str(post.id), 'shared_by': str(user.id)}
            shared_posts_all.append(new_share)
            insert_statement = posts_shared_association.insert().values(new_share)
            session.execute(insert_statement)
            session.commit()
    formated_shares = []
    for shared_post in shared_posts_all:
        formated_data = json.dumps(
            {
                'post_id': shared_post['shared_post'],
                'user_id': shared_post['shared_by'],
                'method': 'ADD',
            }
        )
        formated_shares.append(formated_data)

    with RabbitMQConnection() as conn:
        for formated_data in formated_shares:
            conn.publish_message('share_post', formated_data)
    session.close()


def create_likes_dislikes(users: list[User], posts: list[Post]):
    session = Session()
    Faker.seed(0)
    likes_dislikes = []
    for user in users:
        posts_random = random.sample(posts, k=3)
        for post in posts_random:
            new_like = LikeDislike(
                reviewed_by_id=user.id,
                reviewed_on_id=post.id,
                review_type=random.choice([True, False]),
            )
            likes_dislikes.append(new_like)
            session.add(new_like)
            session.commit()
            session.refresh(new_like)

    with RabbitMQConnection() as conn:
        for like_dislike in likes_dislikes:
            conn.publish_message('crud_operations', like_dislike.format_for_rabbit('CREATE'))

    session.close()


def create_events(users: list[User]):
    session = Session()
    Faker.seed(0)
    prague_timezone = pytz.timezone('Europe/Prague')

    def generate_event():
        fake_datetime = datetime.datetime(
            2024,
            month=random.randint(1, 12),
            day=random.randint(1, 28),
            hour=random.randint(1, 23),
            minute=random.randint(1, 59),
            second=random.randint(1, 59),
            microsecond=0,
            tzinfo=prague_timezone,
        )
        return Event(
            name=fake.sentence(),
            description=fake.paragraph(nb_sentences=5),
            event_pict=f"/path/to/{fake.word()}.jpg",
            capacity=random.randint(10, 25),
            event_datetime=fake_datetime,
            created_event_id=random.choice(users).id,
        )

    events = [generate_event() for _ in range(10)]
    session.add_all(events)
    session.commit()
    for event in events:
        session.refresh(event)

    with RabbitMQConnection() as conn:
        for event in events:
            conn.publish_message('crud_operations', event.format_for_rabbit('CREATE'))
    session.close()
    return events


def create_attending_users(users: list[User], events: list[Event]):
    session = Session()
    inserts_formated = []
    for event in events:
        attending_users = random.sample(users, k=random.randint(1, 10))
        for user in attending_users:
            formated_insert = {'user_attending': user.id, 'on_event': event.id}
            insert_statement = event_attending_associations.insert().values(formated_insert)
            inserts_formated.append(formated_insert)
            session.execute(insert_statement)
            session.commit()

    with RabbitMQConnection() as conn:
        for insert in inserts_formated:
            conn.publish_message(
                'events',
                json.dumps(
                    {
                        'method': 'REGISTER',
                        'user_id': str(insert['user_attending']),
                        'event_id': str(insert['on_event']),
                        'model': 'events',
                    }
                ),
            )
    session.close()


def create_follows(users: list[User]):
    session = Session()
    followers = []
    for user in users:
        users_without_user = [user_tmp for user_tmp in users if user_tmp.id != user.id]
        for random_user in random.sample(users_without_user, k=5):
            follow_insert = {'follower_id': str(user.id), 'followed_id': str(random_user.id)}
            insert_statement = user_followers_association.insert().values(
                follow_insert
            )
            followers.append(follow_insert)
            session.execute(insert_statement)        
    session.commit()
    with  RabbitMQConnection() as conn:
        for follow in followers:
            data_for_rabbit = json.dumps(
                {
                    'follower_id':follow['follower_id'],
                    'followed_id':follow['followed_id'],
                    'method':'ADD'
                }
            )
            conn.publish_message('follow_user',data_for_rabbit)
    session.close()