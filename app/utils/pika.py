import pika

credentials = pika.PlainCredentials('admin', 'admin')

def pika_connect(reciever: bool = False) -> pika.BlockingChannel:
    connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', credentials=credentials)
    )
    channel = connection.channel()
    declare_queues(channel)
    if reciever:
        handle_queues(channel)
    return channel
    

def declare_queues(channel):
    for queue in queues_with_callbacks.keys():
        channel.queue_declare(queue=queue)


def publish_message(channel, queue, message):
    channel.basic_publish(exchange='', routing_key=queue, body=message)
    # Close the connection


def handle_queues(channel):
    for queue, callback in queues_with_callbacks.items():
        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)


# ---------------------------------------------------------
# Callbacks
# ---------------------------------------------------------
def hello_callback(ch, method, properties, body):
    print(f" [x] Received {body}")


# ---------------------------------------------------------
# Queues
# ---------------------------------------------------------
queues_with_callbacks = {'hello': hello_callback}
