from pymongo import MongoClient

local_connection_string = ""

client = MongoClient("mongodb://admin:admin@127.0.0.1:27017/")
try:
    client.admin.command('ping')
    print("Pinged your deployment. You have successfully connected to MongoDB!")
except Exception as e:
    print(e)

mongo_db = client["social_db"]