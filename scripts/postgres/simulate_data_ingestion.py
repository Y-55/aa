import os
from dotenv import load_dotenv
import psycopg2
import pandas as pd
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import uuid
import numpy as np
from sys import argv
import time

load_dotenv()

DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')


def simulate_data_ingestion(n_content, n_events, n_pause_time_seconds, simulation_time_seconds):
    # Create SQLAlchemy engine
    engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    start_time = time.time()  # Record the start time
    time_limit = simulation_time_seconds  # Set the time limit in seconds
    
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > time_limit:
            print(f"Script reached time limit of {time_limit} seconds. Exiting.")
            break

        # Your script's main logic goes here
        # This example just prints the elapsed time
        print(f"Elapsed time: {elapsed_time:.2f} seconds")
        time.sleep(1) # Simulate some work or a delay

        # Generate dummy content data
        content_ids = [str(uuid.uuid4()) for _ in range(n_content)]
        slugs = [str(uuid.uuid4()) for _ in range(n_content)]
        content_types = ['podcast', 'newsletter', 'video']
        now = datetime.utcnow()
        content_df = pd.DataFrame({
            'id': content_ids,
            'slug': slugs,
            'title': [f"Title {i}" for i in range(n_content)],
            'content_type': [random.choice(content_types) for _ in range(n_content)],
            'length_seconds': np.random.randint(60, 3600, n_content),
            'publish_ts': [now - timedelta(days=random.randint(0, 365)) for _ in range(n_content)]
        })

        # Insert content data
        content_df.to_sql('content', engine, if_exists='append', index=False, method='multi')
        print(f"Inserted {n_content} rows into 'content' table.")

        # Generate dummy engagement_events data
        event_types = ['play', 'pause', 'finish', 'click']
        devices = ['ios', 'android', 'web-safari', 'web-chrome']
        user_ids = [str(uuid.uuid4()) for _ in range(n_content)]
        engagement_df = pd.DataFrame({
            'content_id': [random.choice(content_ids) for _ in range(n_events)],
            'user_id': [random.choice(user_ids) for _ in range(n_events)],
            'event_type': [random.choice(event_types) for _ in range(n_events)],
            'event_ts': [now for _ in range(n_events)],
            'duration_ms': [random.choice([None, random.randint(100, 10000)]) for _ in range(n_events)],
            'device': [random.choice(devices) for _ in range(n_events)],
            'raw_payload': [None for _ in range(n_events)]
        })

        # Insert engagement_events data
        engagement_df.to_sql('engagement_events', engine, if_exists='append', index=False, method='multi')
        print(f"Inserted {n_events} rows into 'engagement_events' table.")

        time.sleep(n_pause_time_seconds)

if __name__ == "__main__":
    # Parse command line arguments
    if len(argv) != 5:
        print("Usage: python simulate_data_ingestion.py <n_content> <n_events> <n_pause_time_seconds> <simulation_time_seconds>")
        exit(1)
    n_content = int(argv[1])
    n_events = int(argv[2])
    n_pause_time_seconds = int(argv[3])
    simulation_time_seconds = int(argv[4])
    simulate_data_ingestion(n_content, n_events, n_pause_time_seconds, simulation_time_seconds)