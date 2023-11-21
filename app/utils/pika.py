import json
from typing import Callable

import pika
from pika.adapters.blocking_connection import BlockingChannel

from .mongo.collections import mongo_collections
from .mongo.custom_methods import add_comment_to_post, add_tags_to_post


class PikaException(Exception):
    def __init__(self, message):
        super().__init__(message)


class RabbitMQConnection:
    credentials: pika.PlainCredentials = pika.PlainCredentials('admin', 'admin')

    def __init__(self, reciever: bool = False):
        self.reciever = reciever

    def __enter__(self) -> BlockingChannel:
        # Establish RabbitMQ connection and channel
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters('localhost', credentials=self.credentials)
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
            self.channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

    def declare_queues(self) -> None:
        for queue in queues_with_callbacks.keys():
            self.channel.queue_declare(queue=queue)

    def publish_message(self, queue, message) -> None:
        if not self.reciever:
            self.channel.basic_publish(exchange='', routing_key=queue, body=json.dumps(message))
        else:
            raise PikaException("Cannot publish message from reciever connection.")


# ---------------------------------------------------------
# Callbacks
# ---------------------------------------------------------
def hello_callback(ch, method, properties, body) -> None:
    print(f" [x] Received {json.loads(body)}")


def info_callback(ch, method, properties, body) -> None:
    print(f" [x] Received: {body.decode('utf-8')}")


status = {True: '\033[92m Succeded! \033[0m', False: '\033[91m Failed! \033[0m'}


def handle_crud_callback(ch, method, properties, body) -> None:
    message = json.loads(json.loads(body))
    print(f" [x] Received {message}")

    collection = mongo_collections[message['model']]
    match message['method']:
        case 'CREATE':
            res = collection.add_document(message['data'])
            print(
                f" [x] Adding document to collection '{message['model']}': {message['data']} {status[res]}"
            )
        case 'UPDATE':
            res = collection.update_document(message['data']['_id'], message['data'])
            print(
                f" [x] Updating document in collection {message['model']} with ID '{message['data']['_id']}': {message['data']} {status[res]}"
            )
        case 'DELETE':
            res = collection.remove_document(message['data']['_id'])
            print(
                f" [x] Removing document from collection {message['model']} with ID '{message['data']['_id']}' {status[res]}"
            )
        case _:
            print(" [x] Shit has happened")


def handle_tags_callback(ch, method, properties, body):
    message = json.loads(json.loads(body))
    match message["method"]:
        case 'ADD':
            res = add_tags_to_post(message['post_id'], message['tags'])
            print(f' [x] Added tags to post {message["post_id"]} - {message["tags"]} {status[res]}')



def handle_comments_callback(ch, method, properties, body):
    message = json.loads(json.loads(body))
    match message['method']:
        case 'ADD':
            res = add_comment_to_post(message['post_id'], message['comment_id'])
            print(
                f' [x] Added comment to post {message["post_id"]} - {message["comment_id"]} {status[res]}'
            )


# ---------------------------------------------------------
# Queues
# ---------------------------------------------------------
queues_with_callbacks: dict[str, Callable[..., None]] = {
    'hello': hello_callback,
    'info': info_callback,
    'crud_operations': handle_crud_callback,
    'tags': handle_tags_callback,
    'comments': handle_comments_callback,
}
