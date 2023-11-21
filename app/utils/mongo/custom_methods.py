from .collections import *


def add_comment_to_post(post_id, comment_id):
    print("POST ID:", post_id)
    print("COMMENT ID: ", comment_id)
    post_from_db = post_collection.find_document({'_id': post_id})
    if not post_from_db:
        return False
    post_from_db['comments'].append(comment_id)
    result = post_collection.update_document(post_id, {'comments': post_from_db['comments']})
    return result


def add_tags_to_post(post_id, tags):
    print("POST ID:", post_id)
    print("TAGS: ", tags)
    post_from_db = post_collection.find_document({'_id': post_id})
    for tag in tags:
        tag_from_mongo = tag_collection.find_document({'_id': tag['_id']})
        if not tag_from_mongo:
            tag_collection.add_document(tag)
        
    result_tags = [tag for tag in post_from_db['tags']]
    for tag_to_add in tags:
        if not (tag_to_add['_id'] in post_from_db['tags']):
            result_tags.append(tag_to_add['_id'])

    result = post_collection.update_document(post_id, {'tags': result_tags})

    return result

