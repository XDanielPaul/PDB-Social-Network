import json
from typing import Callable

import pika
from pika.adapters.blocking_connection import BlockingChannel


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


# ---------------------------------------------------------
# Queues
# ---------------------------------------------------------
queues_with_callbacks: dict[str, Callable[..., None]] = {
    'hello': hello_callback, 'info': info_callback}
