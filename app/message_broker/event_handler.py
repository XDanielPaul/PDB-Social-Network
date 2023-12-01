import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.pika import RabbitMQConnection

# Create a connection to RabbitMQ and start consuming messages on all queues
if __name__ == '__main__':
    with RabbitMQConnection(reciever=True) as conn:
        print(' [*] Waiting for messages. To exit, press CTRL+C')
        # Start consuming messages from the 'hello' queue
        conn.channel.start_consuming()
