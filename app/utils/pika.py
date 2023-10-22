from typing import Callable
import pika
from pika.adapters.blocking_connection import BlockingChannel

credentials: pika.PlainCredentials = pika.PlainCredentials('admin', 'admin')


def pika_connect(reciever: bool = False) -> BlockingChannel:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost', credentials=credentials)
    )
    channel = connection.channel()
    declare_queues(channel)
    if reciever:
        handle_queues(channel)
    return channel


def declare_queues(channel) -> None:
    for queue in queues_with_callbacks.keys():
        channel.queue_declare(queue=queue)


def publish_message(channel, queue, message) -> None:
    channel.basic_publish(exchange='', routing_key=queue, body=message)

def handle_queues(channel) -> None:
    for queue, callback in queues_with_callbacks.items():
        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)


# ---------------------------------------------------------
# Callbacks
# ---------------------------------------------------------
def hello_callback(ch, method, properties, body) -> None:
    print(f" [x] Received {body}")


# ---------------------------------------------------------
# Queues
# ---------------------------------------------------------
queues_with_callbacks: dict[str,Callable[..., None]] = {
    'hello': hello_callback
}
