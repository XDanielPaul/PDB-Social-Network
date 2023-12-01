from app.utils.mongo.collections import *


# Expand ids of user attributes to objects -> Level 1 expansion
def expand_ids_to_objects_user(users: list[dict]) -> list[dict]:
    for user in users:
        user['followers'] = user_collection.find_documents({'_id': {'$in': user['followers']}})
        user['follows'] = user_collection.find_documents({'_id': {'$in': user['follows']}})
        user['postIds'] = post_collection.find_documents({'created_by_id': user['_id']})
        user['shared_posts'] = post_collection.find_documents({'created_by_id': user['_id']})
        user['attending_events'] = event_collection.find_documents(
            {'_id': {'$in': user['attending_events']}}
        )
    return users


# Expand ids of post attributes to objects -> Level 1 expansion
def expand_ids_to_objects_post(posts: list[dict]) -> list[dict]:
    for post in posts:
        post['comments'] = comment_collection.find_documents({'on_post_id': post['_id']})
        post['shared_by_users'] = user_collection.find_documents({'shared_posts': post['_id']})
        post['likes_dislikes'] = like_dislike_collection.find_documents(
            {'reviewed_on_id': post['_id']}
        )
        post['tags'] = tag_collection.find_documents({'_id': {'$in': post['tags']}})
    return posts


# Expand ids of comment attributes to objects -> Level 1 expansion
def expand_ids_to_objects_event(events: list[dict]) -> list[dict]:
    for event in events:
        if event.get('attending_users'):
            event['attending_users'] = user_collection.find_documents(
                {'_id': {'$in': event['attending_users']}}
            )
    return events
