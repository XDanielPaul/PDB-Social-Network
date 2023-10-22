import os
import sys

# TODO: Fix imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.pika import pika_connect

pika_channel = pika_connect(reciever=True)

print(' [*] Waiting for messages. To exit, press CTRL+C')
# Start consuming messages from the 'hello' queue
pika_channel.start_consuming()
