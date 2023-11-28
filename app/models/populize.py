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

# TODO
# [DONE] Create users
# [DONE] Create posts and tags
# [DONE] Create some shared posts
# [DONE] Create some comments
# [DONE] Create some likes and dislikes
# [DONE] Create some events
# [DONE] Create some attending users to events

sys.path.append('../')
from utils.pika import RabbitMQConnection

connection_string = "postgresql://admin:admin@localhost:5432/db_name"
engine = create_engine(connection_string, echo=True)
Session = sessionmaker(bind=engine)
fake = Faker()


def create_users():
    session = Session()
    path_to_file = './example_data/users.json'
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
    session.refresh(tags)
    # adding posts to the database
    posts = [generate_post() for _ in range(10)]
    session.add_all(posts)
    session.commit()
    session.refresh(posts)
    tags_and_posts = {f"{post.id}": [] for post in posts}

    # adding tags to posts in Postgre
    for post in posts:
        for tag in random.choices(tags, k=3):
            tags_and_posts[f"{post.id}"].append(tag)
            insert_statement = tags_posts_associations.insert().values(
                {'tag_name': tag.id, 'tag_post': post.id}
            )
            session.execute(insert_statement)
    session.commit()
    # adding post and its tags to the mongo
    for post in posts:
        formated_data = post.format_for_rabbit('CREATE')
        tags = {'post_id': str(post.id), 'tags': tags_and_posts[f"{post.id}"], 'method': 'ADD'}
        with RabbitMQConnection() as conn:
            conn.publish_message('crud_operations', formated_data)
            conn.publish_message('tags', json.dumps(tags))

    session.close()
    return posts


def create_comments(users: list[User], posts: list[Post]):
    sesion = Session()
    Faker.seed(0)
    formated_comments_rabbit = []
    comment_objects = []
    for user in users:
        posts_random = random.choices(posts, k=3)
        for post in posts_random:
            new_comment = Comment(
                content=fake.sentence(random_seed=12), created_by_id=user.id, on_post_id=post.id
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
    shared_posts = []
    for user in users:
        shared_posts = random.choices(posts, k=2)
        for post in shared_posts:
            new_share = {'shared_post': post.id, 'shared_by': user.id}
            shared_posts.append(new_share)
            insert_statement = posts_shared_association.insert().values(new_share)
            session.execute(insert_statement)
            session.commit()
    formated_shares = []
    for shared_post in shared_posts:
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
            conn.publish_message('shared_posts', formated_data)
    session.close()


def create_likes_dislikes(users: list[User], posts: list[Post]):
    session = Session()
    Faker.seed(0)
    likes_dislikes = []
    for user in users:
        posts_random = random.choices(posts, k=3)
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
    start_date = datetime.datetime(2024, 1, 1, 0, 0, 0, 0)
    end_date = datetime.datetime(2025, 1, 1, 0, 0, 0, 0)

    def generate_event():
        return Event(
            name=fake.sentence(),
            description=fake.paragraph(nb_sentences=5),
            event_pict=f"/path/to/{fake.word()}.jpg",
            capacity=random.randint(10, 25),
            event_datetime=fake.date_time_between(
                datetime_start=start_date, datetime_end=end_date, tzinfo=None
            ),
            created_event_id=random.choice(users).id,
        )

    events = [generate_event() for _ in range(10)]
    session.add_all(events)
    session.commit()
    session.refresh(events)

    with RabbitMQConnection() as conn:
        for event in events:
            conn.publish_message('crud_operations', event.format_for_rabbit('CREATE'))
    session.close()
    return events


def create_attending_users(users: list[User], events: list[Event]):
    session = Session()
    inserts_formated = []
    for event in events:
        attending_users = random.choices(users, k=random.randint(1, 10))
        for user in attending_users:
            formated_insert = {{'user_attending': user.id, 'on_event': event.id}}
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
                        'event_id': str(insert['event_id']),
                        'model': 'events',
                    }
                ),
            )
    session.close()


if __name__ == "__main__":
    # Database reset
    UUIDBase.metadata.drop_all(engine)
    UUIDBase.metadata.create_all(engine)

    while True:
        question = input('What do you want? (Y for generating all data)')

        if question == "Y":
            generated_users = create_users()
            posts = create_posts(generated_users)
            create_comments(generated_users, posts)
            create_shared_posts(generated_users, posts)
            create_likes_dislikes(generated_users, posts)
            events = create_events(generated_users)
            create_attending_users(generated_users, events)
            break
