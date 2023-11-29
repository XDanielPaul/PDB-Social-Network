import requests

# QUERY


def test_get_posts(headers):
    r = requests.get(
        'http://localhost:8001/posts',
        headers=headers,
    )
    assert r.status_code == 200
    assert any(post['content'] == 'test' for post in r.json())


def test_get_post(headers, post_id):
    r = requests.get(
        f'http://localhost:8001/posts/{post_id}',
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()[0]['content'] == 'test'


def test_get_posts_by_tags(headers):
    r = requests.get(
        'http://localhost:8001/posts/tags?tags=Test',
        headers=headers,
    )
    assert r.status_code == 200
    assert any(post['content'] == 'test' for post in r.json())


def test_get_posts_by_likes_dislikes(headers):
    r = requests.get(
        'http://localhost:8001/posts/rate_filter',
        headers=headers,
    )
    assert r.status_code == 200
    # Test post is without the rating, so it should be last
    assert r.json()[-1]['content'] == 'test'


def test_get_my_posts(headers):
    r = requests.get(
        'http://localhost:8001/posts/my_posts',
        headers=headers,
    )
    assert r.status_code == 200
    assert any(post['content'] == 'test' for post in r.json())


def test_get_my_feed(headers):
    r = requests.get(
        'http://localhost:8001/posts/my_feed',
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json() == []


# COMMAND


def test_create_delete_post(headers):
    r = requests.post(
        'http://localhost:8000/posts',
        headers=headers,
        json={
            'title': 'test',
            'content': 'test',
            'tags': [],
        },
    )
    assert r.status_code == 201

    post_id = r.json()['id']

    r = requests.delete(
        f'http://localhost:8000/posts/{post_id}',
        headers=headers,
    )
    assert r.status_code == 200


def test_share_post(headers):
    r = requests.post(
        'http://localhost:8000/posts',
        headers=headers,
        json={
            'title': 'test',
            'content': 'test',
            'tags': [],
        },
    )

    post_id = r.json()['id']

    r = requests.post(
        f'http://localhost:8000/posts/share/{post_id}?share=true',
        headers=headers,
    )
    assert r.status_code == 201

    r = requests.post(
        f'http://localhost:8000/posts/share/{post_id}?share=true',
        headers=headers,
    )
    assert r.status_code == 409
    assert r.json()['detail'] == 'You already shared this post.'

    r = requests.post(
        f'http://localhost:8000/posts/share/{post_id}?share=false',
        headers=headers,
    )
    assert r.status_code == 201

    r = requests.post(
        f'http://localhost:8000/posts/share/{post_id}?share=false',
        headers=headers,
    )
    assert r.status_code == 409
    assert r.json()['detail'] == "You didn't share this post."

    r = requests.delete(
        f'http://localhost:8000/posts/{post_id}',
        headers=headers,
    )
    assert r.status_code == 200


def test_like_post(headers):
    r = requests.post(
        'http://localhost:8000/posts',
        headers=headers,
        json={
            'title': 'test',
            'content': 'test',
            'tags': [],
        },
    )

    post_id = r.json()['id']

    r = requests.post(
        f'http://localhost:8000/posts/like-dislike/',
        json={
            'post_id': post_id,
            'like': True,
        },
        headers=headers,
    )
    assert r.status_code == 201

    r = requests.post(
        f'http://localhost:8000/posts/like-dislike/',
        json={
            'post_id': post_id,
            'like': True,
        },
        headers=headers,
    )
    assert r.status_code == 409
    assert r.json()['detail'] == 'This user already reviewed this post.'

    r = requests.delete(
        f'http://localhost:8000/posts/like-dislike/{post_id}',
        headers=headers,
    )

    r = requests.delete(
        f'http://localhost:8000/posts/{post_id}',
        headers=headers,
    )
    assert r.status_code == 200
