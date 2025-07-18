import os
import json
import requests
from dotenv import load_dotenv
from kafka.admin import KafkaAdminClient


load_dotenv()

REDPANDA_HOST = os.getenv('REDPANDA_HOST')
REDPANDA_BROKER_PORT = os.getenv('REDPANDA_BROKER_PORT')

def clear_topics():
    admin_client = KafkaAdminClient(
        bootstrap_servers=f"{REDPANDA_HOST}:{REDPANDA_BROKER_PORT}",
        client_id="clear_topics"
    )
    topics = admin_client.list_topics()
    print(topics)
    for topic in topics:
        if topic.startswith('pg') or topic.startswith('ch'):
            print(f"Deleting topic: {topic}")
            admin_client.delete_topics([topic])
            print(f"Deleted topic: {topic}")

if __name__ == "__main__":
    clear_topics()