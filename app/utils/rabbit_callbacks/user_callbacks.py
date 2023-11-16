from utils.mongo_connection.mongo_connect import mongo_db



def upload_user(user_obj):
    user_obj['_id'] = user_obj['id']
    del user_obj['id']
    del user_obj['method']
    try:
        mongo_db.users.insert_one(user_obj)
    except:
        return False
    return True