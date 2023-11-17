from .mongo_connect import mongo_db


def add_tags_to_post(post_id, tags):
    print("POST ID:", post_id)
    print("TAGS: ", tags)
    post_from_db = mongo_db.posts.find_one({'_id': post_id})
    for tag in tags:
        tag_from_mongo = mongo_db.tags.find_one({'_id': tag['_id']})
        if not tag_from_mongo:
            mongo_db.tags.insert_one(tag)
    result_tags = [tag for tag in post_from_db['tags']]
    for tag_to_add in tags:
        if not (tag_to_add['_id'] in post_from_db['tags']):
            result_tags.append(tag_to_add['_id'])

    result = mongo_db.posts.update_one(
        {'_id': post_id}, {'$set': {'tags': result_tags}})
    if result.modified_count > 0:
        return True
    else:
        return False
