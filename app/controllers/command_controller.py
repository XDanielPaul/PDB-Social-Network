import os
import sys

import pika

# TODO: Fix imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from litestar import Litestar, get

from ..utils.pika import pika_connect, publish_message


@get("/")
async def hello_world() -> str:
    # Publish the message to the 'hello' queue
    publish_message(pika_channel, 'hello', 'Hello from Controller!')
    return "Hello, Controller!"


app = Litestar([hello_world])
pika_channel = pika_connect()
