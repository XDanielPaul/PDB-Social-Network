import pytest
import requests


@pytest.fixture(autouse=True)
def setup():
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

    r = requests.post(
        'http://localhost:8000/users/login',
        json={
            "username": "test",
            "password": "test",
        },
    )
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}

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

    yield

    requests.delete(
        f'http://localhost:8000/event/{event_id}',
        headers=headers,
    )

    requests.delete(
        f'http://localhost:8000/posts/{post_id}',
        headers=headers,
    )

    requests.delete(
        f'http://localhost:8000/users/{user_id}',
        headers=headers,
    )


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


@pytest.fixture
def id(headers):
    r = requests.get(
        'http://localhost:8001/users',
        headers=headers,
    )
    users = [user if user['username'] == 'test' else None for user in r.json()]
    return [user for user in users if user is not None][0]['_id']


@pytest.fixture
def post_id(headers):
    r = requests.get(
        'http://localhost:8001/posts',
        headers=headers,
    )
    posts = [post if post['title'] == 'test' else None for post in r.json()]
    return [post for post in posts if post is not None][0]['_id']


@pytest.fixture
def event_id(headers):
    r = requests.get(
        'http://localhost:8001/events',
        headers=headers,
    )
    events = [event if event['name'] == 'test' else None for event in r.json()]
    return [event for event in events if event is not None][0]['_id']


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
