from utils.mongo_connection.mongo_connect import mongo_db



def upload_user(user_obj):
    try:
        mongo_db.users.insert_one(user_obj)
    except:
        return False
    return True

def delete_user(user_obj):
    print(user_obj)
    try:
        result = mongo_db.users.delete_one({'_id':user_obj.get('id')})
        if result.deleted_count == 1:
            return True
        return False
    except Exception as err:
        print(err)
        return False