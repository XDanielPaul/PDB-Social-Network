import os
import sys

import pika

# TODO: Fix imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from litestar import Litestar, get

from ..utils.pika import credentials, declare_queues, publish_message


@get("/")
async def hello_world() -> str:
    # Publish the message to the 'hello' queue
    publish_message(channel, 'hello', 'Hello from Controller!')
    return "Hello, Controller!"


app = Litestar([hello_world])
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', credentials=credentials)
)
channel = connection.channel()

declare_queues(channel)
