from pymongo.collection import Collection

from .mongo_connect import mongo_db


class CollectionController:
    def __init__(self, collection):
        self.collection: Collection = collection

    def add_document(self, document) -> bool:
        result = self.collection.insert_one(document)
        return result.acknowledged

    def update_document(self, document_id, update_data) -> bool:
        filter_query = {"_id": document_id}
        update_query = {"$set": update_data}
        result = self.collection.update_one(filter_query, update_query)
        return result.acknowledged and result.modified_count > 0

    def remove_document(self, document_id) -> bool:
        filter_query = {"_id": document_id}
        result = self.collection.delete_one(filter_query)
        return result.acknowledged and result.deleted_count > 0

    def find_document(self, query):
        return self.collection.find_one(query)

    def find_documents(self, query):
        return list(self.collection.find(query))


user_collection = CollectionController(mongo_db['users'])
post_collection = CollectionController(mongo_db['posts'])
comment_collection = CollectionController(mongo_db['comments'])
tag_collection = CollectionController(mongo_db['tags'])
event_collection = CollectionController(mongo_db['events'])
like_dislike_collection = CollectionController(mongo_db['like_dislike'])  # ???

mongo_collections = {
    "users": user_collection,
    "posts": post_collection,
    "comments": comment_collection,
    "tags": tag_collection,
    "events": event_collection,
    "like_dislike": like_dislike_collection,
}
