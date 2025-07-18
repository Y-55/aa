import os
import json
import requests
from dotenv import load_dotenv

# Get the absolute path to the project root (assuming this script is always in scripts/redpanda/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

load_dotenv()

DEBEZIUM_HOST = os.getenv('DEBEZIUM_HOST')
DEBEZIUM_PORT = os.getenv('DEBEZIUM_PORT')

config_path = os.path.join(PROJECT_ROOT, 'configs', 'debezium_postgres_connect.json')

print(f"Config path: {config_path}")

def init_postgres_connect():
    url = f"http://{DEBEZIUM_HOST}:{DEBEZIUM_PORT}/connectors"
    headers = {
        "Content-Type": "application/json"
    }
    data = json.load(open(config_path))
    response = requests.post(url, headers=headers, json=data)
    print(response.json())

if __name__ == "__main__":
    init_postgres_connect()