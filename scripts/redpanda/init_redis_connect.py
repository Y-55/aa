import os
import json
import requests
from dotenv import load_dotenv

# Get the absolute path to the project root (assuming this script is always in scripts/redpanda/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

load_dotenv()

REDIS_CONNECT_HOST = os.getenv('REDIS_CONNECT_HOST')
REDIS_CONNECT_PORT = os.getenv('REDIS_CONNECT_PORT')

config_path = os.path.join(PROJECT_ROOT, 'configs', 'redis_connect.json')

print(f"Config path: {config_path}")

def init_redis_connect():
    url = f"http://{REDIS_CONNECT_HOST}:{REDIS_CONNECT_PORT}/connectors"
    headers = {
        "Content-Type": "application/json"
    }
    data = json.load(open(config_path))
    response = requests.post(url, headers=headers, json=data)
    print(response.json())

if __name__ == "__main__":
    init_redis_connect()