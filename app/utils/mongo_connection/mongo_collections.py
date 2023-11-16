def create_mongo_user(user_obj):
    mongo_user = {
        '_id' :  user_obj.get('id'),
        'username' : user_obj.get('username'),
        'password' : user_obj.get('password'),
        'profile_picture' : user_obj.get('profile_picture'),
        'profile_bio' : user_obj.get('profile_bio'),
        'postInfoIds' : [],
        'followers' : [],
        'follows' : [],
        'shared_posts' : [],
        'attending_events' : []
    }
    return mongo_user

def create_mongo_post(post_obj):
    mongo_post = {
        '_id' :  post_obj.get('id'),
        'title' : post_obj.get('title'),
        'content' : post_obj.get('content'),
        'image_ref' : post_obj.get('image_ref'),
        'created_by' : post_obj.get('created_by_id'),
        'created_at' : post_obj.get('created_at'),
        'updated_at' : post_obj.get('updated_at'),
        'tags' : [], # TODO: Add tags later
        'comments' : [],
        'shared_by' : []
    }
    return mongo_post