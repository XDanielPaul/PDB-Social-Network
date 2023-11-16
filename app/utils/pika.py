import json
from typing import Callable
import os
import sys
import pika
from pika.adapters.blocking_connection import BlockingChannel
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from app.utils.rabbit_callbacks.user_callbacks import upload_user,delete_user
from app.utils.mongo_connection.mongo_collections import create_mongo_user,create_mongo_post
class PikaException(Exception):
    def __init__(self, message):
        super().__init__(message)


class RabbitMQConnection:
    credentials: pika.PlainCredentials = pika.PlainCredentials(
        'admin', 'admin')

    def __init__(self, reciever: bool = False):
        self.reciever = reciever

    def __enter__(self) -> BlockingChannel:
        # Establish RabbitMQ connection and channel
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    'localhost', credentials=self.credentials)
            )
            self.channel = self.connection.channel()
        except:
            raise PikaException("Cannot connect to RabbitMQ.")
        self.declare_queues()
        if self.reciever:
            self.handle_queues()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Close RabbitMQ connection after publishing
        self.connection.close()

    def handle_queues(self) -> None:
        for queue, callback in queues_with_callbacks.items():
            self.channel.basic_consume(
                queue=queue, on_message_callback=callback, auto_ack=True)

    def declare_queues(self) -> None:
        for queue in queues_with_callbacks.keys():
            self.channel.queue_declare(queue=queue)

    def publish_message(self, queue, message) -> None:
        if not self.reciever:
            self.channel.basic_publish(
                exchange='', routing_key=queue, body=json.dumps(message))
        else:
            raise PikaException(
                "Cannot publish message from reciever connection.")


# ---------------------------------------------------------
# Callbacks
# ---------------------------------------------------------
def hello_callback(ch, method, properties, body) -> None:
    print(f" [x] Received {json.loads(body)}")


def info_callback(ch, method, properties, body) -> None:
    print(f" [x] Received: {body.decode('utf-8')}")

def user_callback(ch,method, properties,body) ->  None:
    data = json.loads(json.loads(body))
    print(f" [x] Received {json.loads(body)}")
    if data['method'] == "CREATE":
        result = upload_user(create_mongo_user(data))
        if result:
            print(f" [x]--------- Uploaded user [{data['id']}] to mongodb")
        else:
            print(f" [x]--------- Upload of user [{data['id']}] failed!")
    elif data['method'] == "DELETE":
        result = delete_user(data)
        if result:
            print(f" [x]--------- Deleted user [{data['id']}] from mongodb")
        else:
            print(f" [x]--------- Deletion of user [{data['id']}] failed!")

# ---------------------------------------------------------
# Queues
# ---------------------------------------------------------
queues_with_callbacks: dict[str, Callable[..., None]] = {
    'hello': hello_callback, 'info': info_callback,'user':user_callback}

