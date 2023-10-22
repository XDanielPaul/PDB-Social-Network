import os
import sys

import pika

# TODO: Fix imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from litestar import Litestar, get

from ..utils.pika import RabbitMQConnection


@get("/")
async def hello_world() -> str:
    # Publish the message to the 'hello' queue
    with RabbitMQConnection() as conn:
        conn.publish_message('hello', 'Hello from Controller!')
    return "Hello, Controller!"


app = Litestar([hello_world])
