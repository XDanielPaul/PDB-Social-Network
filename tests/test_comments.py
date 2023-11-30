import requests

# QUERY


def test_get_comments(headers):
    r = requests.get(
        'http://localhost:8001/comments',
        headers=headers,
    )
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_comment(headers, comment_id):
    r = requests.get(
        f'http://localhost:8001/comments/{comment_id}',
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()['content'] == 'test'


def test_get_comments_on_post(headers, post_id):
    r = requests.get(
        f'http://localhost:8001/comments/post_comments/{post_id}',
        headers=headers,
    )
    assert r.status_code == 200
    assert len(r.json()) >= 1


# COMMAND


def test_create_delete_comment(headers, post_id):
    r = requests.post(
        'http://localhost:8000/comments',
        headers=headers,
        json={
            "content": "test",
            "on_post_id": post_id,
        },
    )
    assert r.status_code == 201
    assert r.json()['Comment']['content'] == 'test'
    comment_id = r.json()['Comment']['_id']

    r = requests.delete(
        f'http://localhost:8000/comments/{comment_id}',
        headers=headers,
    )
    assert r.status_code == 200


def test_update_comment(headers, comment_id):
    r = requests.get(
        f'http://localhost:8001/comments/{comment_id}',
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()['content'] == 'test'

    r = requests.put(
        'http://localhost:8000/comments',
        headers=headers,
        json={
            "id": comment_id,
            "content": "test2",
        },
    )
    assert r.status_code == 200
    assert r.json()['return'] == True

    r = requests.get(
        f'http://localhost:8001/comments/{comment_id}',
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()['content'] == 'test2'
