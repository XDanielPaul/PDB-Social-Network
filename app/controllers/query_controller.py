from litestar import Litestar, get

import motor.motor_asyncio as motor

local_connection_string = ""

client = motor.AsyncIOMotorClient("mongodb://admin:admin@127.0.0.1:27017/")
try:
    client.admin.command('ping')
    print("Pinged your deployment. You have successfully connected to MongoDB!")
except Exception as e:
    print(e)

mongo_db = client["social_db"]

@get("/")
async def hello_world() -> str:
    return "Hello, Query!"


app = Litestar([hello_world])
