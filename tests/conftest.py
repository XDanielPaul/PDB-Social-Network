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
    id = r.json()['id']
    yield
    r = requests.post(
        'http://localhost:8000/users/login',
        json={
            "username": "test",
            "password": "test",
        },
    )
    token = r.json()['token']
    headers = {'Authorization': f'Bearer {token}'}

    r = requests.delete(
        f'http://localhost:8000/users/{id}',
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
        'http://localhost:8000/users',
        headers=headers,
    )
    users = [user if user['username'] == 'test' else None for user in r.json()]
    return [user for user in users if user is not None][0]['id']
