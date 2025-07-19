import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

REDIS_CONNECT_HOST = os.getenv('REDIS_CONNECT_HOST')
REDIS_CONNECT_PORT = os.getenv('REDIS_CONNECT_PORT')

def clear_connectors():
    # Get all connectors
    url = f"http://{REDIS_CONNECT_HOST}:{REDIS_CONNECT_PORT}/connectors"
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    print(response.json())
    connectors = response.json()
    for connector in connectors:
        print(connector)
        url = f"http://{REDIS_CONNECT_HOST}:{REDIS_CONNECT_PORT}/connectors/{connector}"
        response = requests.delete(url, headers=headers)

if __name__ == "__main__":
    clear_connectors()