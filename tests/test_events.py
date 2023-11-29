import requests

# QUERY


def test_get_events(headers):
    r = requests.get(
        'http://localhost:8001/events',
        headers=headers,
    )
    assert r.status_code == 200
    assert any(event['name'] == 'test' for event in r.json())


def test_get_event(headers, event_id):
    r = requests.get(
        f'http://localhost:8001/events/{event_id}',
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()[0]['name'] == 'test'


def test_get_event_participants(headers, event_id):
    r = requests.get(
        f'http://localhost:8001/events/{event_id}/participants',
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json() == []

    r = requests.post(
        f'http://localhost:8000/event/attend/{event_id}',
        headers=headers,
    )

    r = requests.get(
        f'http://localhost:8001/events/{event_id}/participants',
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json() != []

    r = requests.post(
        f'http://localhost:8000/event/leave/{event_id}',
        headers=headers,
    )


def test_my_events(headers):
    r = requests.get('http://localhost:8001/events/my_events', headers=headers)
    assert r.status_code == 200
    assert r.json() == []


def test_my_attending_events(headers, event_id):
    r = requests.get('http://localhost:8001/events/my_attending', headers=headers)
    assert r.status_code == 200
    assert r.json() == []

    r = requests.post(
        f'http://localhost:8000/event/attend/{event_id}',
        headers=headers,
    )

    r = requests.get('http://localhost:8001/events/my_attending', headers=headers)
    assert r.status_code == 200
    assert r.json() != []

    r = requests.post(
        f'http://localhost:8000/event/leave/{event_id}',
        headers=headers,
    )


# COMMAND
def test_create_delete_event(headers):
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

    assert r.status_code == 201

    r = requests.delete(
        f'http://localhost:8000/event/{r.json()["id"]}',
        headers=headers,
    )
    assert r.status_code == 200


def test_attend_leave_event(headers, event_id):
    r = requests.post(
        f'http://localhost:8000/event/attend/{event_id}',
        headers=headers,
    )
    assert r.status_code == 201

    r = requests.post(
        f'http://localhost:8000/event/attend/{event_id}',
        headers=headers,
    )
    r.status_code == 409
    r.json()['detail'] == "User is already registered to this event."

    r = requests.post(
        f'http://localhost:8000/event/leave/{event_id}',
        headers=headers,
    )
    assert r.status_code == 201


def test_event_max_capacity(headers, event_id, create_attend_user_id, create_attend_user_id2):
    r = requests.post(
        f'http://localhost:8000/event/attend/{event_id}',
        headers=headers,
    )

    assert r.status_code == 409
    assert r.json()['detail'] == "There is no space for you in this event."

    r = requests.delete(
        f'http://localhost:8000/users/{create_attend_user_id}',
        headers=headers,
    )
    assert r.status_code == 200

    r = requests.delete(
        f'http://localhost:8000/users/{create_attend_user_id2}',
        headers=headers,
    )
    assert r.status_code == 200
