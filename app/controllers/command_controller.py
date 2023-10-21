import sys
import os
import pika
# TODO: Fix imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ..utils.pika import publish_message, declare_queues, credentials
from litestar import Litestar, get

@get("/")
async def hello_world() -> str:
    # Publish the message to the 'hello' queue
    publish_message(channel, 'hello', 'Hello from Controller!')
    return "Hello, Controller!"

app = Litestar([hello_world])
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()

declare_queues(channel)
