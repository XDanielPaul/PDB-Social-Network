import os
import sys
from app.utils.pika import RabbitMQConnection

with RabbitMQConnection(reciever=True) as conn:
    print(' [*] Waiting for messages. To exit, press CTRL+C')
    # Start consuming messages from the 'hello' queue
    conn.channel.start_consuming()
