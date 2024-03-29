import pytest
import requests


@pytest.fixture(autouse=True)
def setup_teardown():
    # SETUP

    # Create a test user
    r = requests.post(
        'http://localhost:8000/users/register',
        json={
            "username": "test",
            "password": "test",
            "profile_picture": "test",
            "profile_bio": "test",
        },
    )
    user_id = r.json()['id']

    # Get the user's token
    r = requests.post(
        'http://localhost:8000/users/login',
        json={
            "username": "test",
            "password": "test",
        },
    )
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}

    # Create a test post
    r = requests.post(
        'http://localhost:8000/posts',
        headers=headers,
        json={
            "title": "test",
            "content": "test",
            "tags": [{"name": "Test"}],
        },
    )

    post_id = r.json()['id']

    # Create a test comment
    r = requests.post(
        'http://localhost:8000/comments',
        headers=headers,
        json={
            "content": "test",
            "on_post_id": post_id,
        },
    )

    comment_id = r.json()['Comment']['_id']

    # Create a test event
    r = requests.post(
        'http://localhost:8000/event',
        headers=headers,
        json={
            "name": "test",
            "description": "test",
            "capacity": 2,
            "event_datetime": "2019-08-24T14:15:22Z",
        },
    )

    event_id = r.json()['id']

    # Do the actual test
    yield

    # TEARDOWN

    # Delete the test event
    requests.delete(
        f'http://localhost:8000/event/{event_id}',
        headers=headers,
    )

    # Delete the test comment
    requests.delete(
        f'http://localhost:8000/comments/{comment_id}',
        headers=headers,
    )

    # Delete the test post
    requests.delete(
        f'http://localhost:8000/posts/{post_id}',
        headers=headers,
    )

    # Delete the test user
    requests.delete(
        f'http://localhost:8000/users/{user_id}',
        headers=headers,
    )


# Get the user's token and return headers for authroized requests
@pytest.fixture
def headers():
    r = requests.post(
        'http://localhost:8000/users/login',
        json={
            "username": "test",
            "password": "test",
        },
    )
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}

    return headers


# Get the user's id
@pytest.fixture
def id(headers):
    r = requests.get(
        'http://localhost:8001/users',
        headers=headers,
    )
    users = [user if user['username'] == 'test' else None for user in r.json()]
    return [user for user in users if user is not None][0]['_id']


# Get the post's id
@pytest.fixture
def post_id(headers):
    r = requests.get(
        'http://localhost:8001/posts',
        headers=headers,
    )
    posts = [post if post['title'] == 'test' else None for post in r.json()]
    return [post for post in posts if post is not None][0]['_id']


# Get the event's id
@pytest.fixture
def event_id(headers):
    r = requests.get(
        'http://localhost:8001/events',
        headers=headers,
    )
    events = [event if event['name'] == 'test' else None for event in r.json()]
    return [event for event in events if event is not None][0]['_id']


# Get the comment's id
@pytest.fixture
def comment_id(headers):
    r = requests.get(
        'http://localhost:8001/comments',
        headers=headers,
    )
    comments = [comment if comment['content'] == 'test' else None for comment in r.json()]
    return [comment for comment in comments if comment is not None][0]['_id']


# Make fake user attend event
@pytest.fixture
def create_attend_user_id(event_id):
    # Create a new user
    r = requests.post(
        'http://localhost:8000/users/register',
        json={
            "username": "test2",
            "password": "test2",
            "profile_picture": "test2",
            "profile_bio": "test2",
        },
    )
    # save user id
    user_id = r.json()['id']
    # Login as the new user
    r = requests.post(
        'http://localhost:8000/users/login',
        json={
            "username": "test2",
            "password": "test2",
        },
    )
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    # Attend event
    r = requests.post(
        f'http://localhost:8000/event/attend/{event_id}',
        headers=headers,
    )
    return user_id


# Make second fake user attend event
@pytest.fixture
def create_attend_user_id2(event_id):
    # Create a new user
    r = requests.post(
        'http://localhost:8000/users/register',
        json={
            "username": "test3",
            "password": "test3",
            "profile_picture": "test3",
            "profile_bio": "test3",
        },
    )
    # save user id
    user_id = r.json()['id']
    # Login as the new user
    r = requests.post(
        'http://localhost:8000/users/login',
        json={
            "username": "test3",
            "password": "test3",
        },
    )
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    # Attend event
    r = requests.post(
        f'http://localhost:8000/event/attend/{event_id}',
        headers=headers,
    )
    return user_id
