import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

DEBEZIUM_HOST = os.getenv('DEBEZIUM_HOST')
DEBEZIUM_PORT = os.getenv('DEBEZIUM_PORT')

def clear_connectors():
    # Get all connectors
    url = f"http://{DEBEZIUM_HOST}:{DEBEZIUM_PORT}/connectors"
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    print(response.json())
    connectors = response.json()
    for connector in connectors:
        print(connector)
        url = f"http://{DEBEZIUM_HOST}:{DEBEZIUM_PORT}/connectors/{connector}"
        response = requests.delete(url, headers=headers)

if __name__ == "__main__":
    clear_connectors()