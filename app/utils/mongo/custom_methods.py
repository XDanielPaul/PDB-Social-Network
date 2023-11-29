from .collections import *

class PikaException(Exception):
    def __init__(self, message):
        super().__init__(message)

def add_comment_to_post(post_id, comment_id):
    post_from_db = post_collection.find_document({'_id': post_id})
    if not post_from_db:
        return False
    post_from_db['comments'].append(comment_id)
    result = post_collection.update_document(post_id, {'comments': post_from_db['comments']})
    return result


def remove_comment_from_post(post_id, comment_id):
    post_from_db = post_collection.find_document({'_id': post_id})
    if not post_from_db:
        return False
    try:
        post_from_db['comments'].remove(comment_id)
    except:
        return False
    result = post_collection.update_document(post_id, {'comments': post_from_db['comments']})
    return result


def follow_user(follower_id, followed_id):
    follower_from_db = user_collection.find_document({'_id': follower_id})
    followed_from_db = user_collection.find_document({'_id': followed_id})
    if not follower_from_db or not followed_from_db:
        return False
    follower_from_db['follows'].append(followed_id)
    followed_from_db['followers'].append(follower_id)
    follower_result = user_collection.update_document(
        follower_id, {'follows': follower_from_db['follows']}
    )
    followed_result = user_collection.update_document(
        followed_id, {'followers': followed_from_db['followers']}
    )
    return follower_result and followed_result


def remove_follow_user(follower_id, followed_id):
    follower_from_db = user_collection.find_document({'_id': follower_id})
    followed_from_db = user_collection.find_document({'_id': followed_id})
    if not follower_from_db or not followed_from_db:
        return False
    try:
        follower_from_db['follows'].remove(followed_id)
    except:
        return False
    try:
        followed_from_db['followers'].remove(follower_id)
    except:
        return False
    follower_result = user_collection.update_document(
        follower_id, {'follows': follower_from_db['follows']}
    )
    followed_result = user_collection.update_document(
        followed_id, {'followers': followed_from_db['followers']}
    )
    return follower_result and followed_result


def add_tags_to_post(post_id, tags):
    post_from_db = post_collection.find_document({'_id': post_id})
    for tag in tags:
        tag_from_mongo = tag_collection.find_document({'_id': tag['_id']})
        if not tag_from_mongo:
            tag_collection.add_document(tag)
    post_from_db["tags"] = post_from_db["tags"] if post_from_db["tags"] else []
    result_tags = [tag for tag in post_from_db['tags']]

    for tag_to_add in tags:
        if not (tag_to_add['_id'] in post_from_db['tags']):
            result_tags.append(tag_to_add['_id'])

    result = post_collection.update_document(post_id, {'tags': result_tags})

    return result


def share_post_by_user(post_id, user_id):
    post_from_db = post_collection.find_document({'_id': post_id})
    if not post_from_db:
        return False
    post_from_db['shared_by_users'].append(user_id)
    post_result = post_collection.update_document(
        post_id, {'shared_by_users': post_from_db['shared_by_users']}
    )

    user_from_db = user_collection.find_document({'_id': user_id})
    if not user_from_db:
        return False
    user_from_db['shared_posts'].append(post_id)
    user_result = user_collection.update_document(
        user_id, {'shared_posts': user_from_db['shared_posts']}
    )
    return post_result and user_result

def add_post_to_user(post_id, user_id):
    result = mongo_db.users.update_one({'_id':user_id},{'$push':{'postIds':post_id}})
    return bool(result)

def remove_post_from_user(post_id, user_id):
    result = mongo_db.users.update_one({'_id':user_id},{'$pull':{'postIds':post_id}})
    return bool(result)

def remove_share_post_by_user(post_id, user_id):
    post_from_db = post_collection.find_document({'_id': post_id})
    if not post_from_db:
        return False
    try:
        post_from_db['shared_by_users'].remove(user_id)
    except:
        return False
    post_result = post_collection.update_document(
        post_id, {'shared_by_users': post_from_db['shared_by_users']}
    )

    user_from_db = user_collection.find_document({'_id': user_id})
    if not user_from_db:
        return False
    try:
        user_from_db['shared_posts'].remove(post_id)
    except:
        return False
    user_result = user_collection.update_document(
        user_id, {'shared_posts': user_from_db['shared_posts']}
    )
    return post_result and user_result

def register_for_event(user_id,event_id):
    event_from_db = event_collection.find_document({'_id':event_id})
    if not event_from_db:
        raise PikaException("Event is not in the database.")
    users = event_from_db.get('attending_users',[])
    capacity = event_from_db.get('capacity',None)
    if len(users) >= capacity:
        raise PikaException("Event is full.")
    users.append(user_id)
    event_result = event_collection.update_document(event_id,{'attending_users':users})

    user_from_db = mongo_db.users.update_one({'_id':user_id},{"$push":{"attending_events":event_id}})
    return bool(event_result) and bool(user_from_db)

def leave_event(user_id,  event_id):
    update_query = {'$pull':{'attending_users':user_id}}
    result1 = mongo_db.events.update_one({'_id':event_id},update_query)
    result2 = mongo_db.users.update_one({'_id':user_id},{"$pull":{"attending_events":event_id}})
    return bool(result1) and bool(result2)
