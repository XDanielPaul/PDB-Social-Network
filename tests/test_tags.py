import requests

# QUERY


def test_get_tags(headers):
    r = requests.get(
        'http://localhost:8001/tags',
        headers=headers,
    )
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_tag(headers, tag_id):
    r = requests.get(
        f'http://localhost:8001/tags/{tag_id}',
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()['name'] == 'Test'


# COMMAND


def test_create_delete_tag(headers):
    r = requests.post(
        'http://localhost:8000/tag',
        headers=headers,
        json={
            "name": "Test2",
        },
    )
    assert r.status_code == 201
    assert r.json()['name'] == 'Test2'
    tag_id = r.json()['id']

    r = requests.delete(
        f'http://localhost:8000/tag/{tag_id}',
        headers=headers,
    )
    assert r.status_code == 200
