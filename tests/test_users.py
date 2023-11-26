import requests


def test_get_users(headers) -> None:
    r = requests.get(
        'http://localhost:8000/users',
        headers=headers,
    )
    assert r.status_code == 200
    assert any(user['username'] == 'test' for user in r.json())


def test_get_user(headers, id) -> None:
    r = requests.get(
        f'http://localhost:8000/users/{id}',
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()['username'] == 'test'


def test_user_update(headers, id) -> None:
    r = requests.get(
        f'http://localhost:8000/users/{id}',
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()['profile_picture'] == 'test'

    r = requests.put(
        f'http://localhost:8000/users',
        headers=headers,
        json={
            "id": id,
            "username": "test",
            "password": "test",
            "profile_picture": "test2",
            "profile_bio": "test2",
        },
    )
    assert r.status_code == 200
    assert r.json()['profile_picture'] == 'test2'

    r = requests.put(
        f'http://localhost:8000/users',
        headers=headers,
        json={
            "id": id,
            "username": "test",
            "password": "test",
            "profile_picture": "test",
            "profile_bio": "test",
        },
    )
    assert r.status_code == 200
    assert r.json()['profile_picture'] == 'test'


def test_create_and_delete(headers):
    r = requests.post(
        'http://localhost:8000/users/register',
        json={
            "username": "test2",
            "password": "test2",
            "profile_picture": "test2",
            "profile_bio": "test2",
        },
    )
    assert r.status_code == 201
    id = r.json()['id']

    r = requests.delete(
        f'http://localhost:8000/users/{id}',
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()['deleted'] == True
    assert r.json()['message'] == f"User with id [{id}] was deleted."


def test_follow(headers):
    r = requests.post(
        'http://localhost:8000/users/register',
        json={
            "username": "test2",
            "password": "test2",
            "profile_picture": "test2",
            "profile_bio": "test2",
        },
    )
    assert r.status_code == 201
    id = r.json()['id']

    r = requests.post(
        f'http://localhost:8000/users/follow/{id}?follow=true',
        headers=headers,
    )

    assert r.status_code == 201
    assert r.json()['followed'] == True

    r = requests.post(
        f'http://localhost:8000/users/follow/{id}?follow=true',
        headers=headers,
    )

    assert r.status_code == 409
    assert r.json()['detail'] == 'You are already following this user.'

    r = requests.post(
        f'http://localhost:8000/users/follow/{id}?follow=false',
        headers=headers,
    )

    assert r.status_code == 201
    assert r.json()['followed'] == False

    r = requests.post(
        f'http://localhost:8000/users/follow/{id}?follow=false',
        headers=headers,
    )

    assert r.status_code == 409
    assert r.json()['detail'] == 'You are not following the user.'

    r = requests.delete(
        f'http://localhost:8000/users/{id}',
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()['deleted'] == True
    assert r.json()['message'] == f"User with id [{id}] was deleted."
