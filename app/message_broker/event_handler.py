import pika
import sys
import os
# TODO: Fix imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.pika import handle_queues, declare_queues, credentials

# Establish a connection to RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()

# Declare the queues
declare_queues(channel)

# Set up a consumer and associate the callback function with the queue
handle_queues(channel)

print(' [*] Waiting for messages. To exit, press CTRL+C')
# Start consuming messages from the 'hello' queue
channel.start_consuming()
