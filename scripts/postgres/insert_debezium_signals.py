import os
import psycopg2
import uuid
import json
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')

def insert_snapshot_signal(table_name, data_collection=None):
    """
    Insert a signal to start an incremental snapshot for the specified table.
    
    Args:
        table_name (str): The table name to snapshot (e.g., 'public.content')
        data_collection (str, optional): The data collection name. If None, uses table_name.
    """
    if data_collection is None:
        data_collection = table_name
    
    signal_id = str(uuid.uuid4())
    signal_data = {
        "type": "execute-snapshot",
        "data": {
            "data-collections": [data_collection],
            "type": "incremental"
        }
    }
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = True
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO debezium_signals (id, type, data) VALUES (%s, %s, %s)",
                (signal_id, signal_data["type"], json.dumps(signal_data["data"]))
            )
        print(f"Signal inserted for table: {table_name}")
        return signal_id
    except Exception as e:
        print(f"Error inserting signal: {e}")
        return None
    finally:
        conn.close()

def main():
    """Main function to insert signals for available tables."""
    available_tables = ['public.content', 'public.engagement_events']
    
    for table in available_tables:
        signal_id = insert_snapshot_signal(table)
        if signal_id:
            print(f"Signal ID: {signal_id}")

if __name__ == "__main__":
    main()
