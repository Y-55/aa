import os
import clickhouse_connect
from dotenv import load_dotenv

load_dotenv()

CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST')
CLICKHOUSE_PORT = os.getenv('CLICKHOUSE_HTTP_PORT')
CLICKHOUSE_USER = os.getenv('CLICKHOUSE_USER')
CLICKHOUSE_PASSWORD = os.getenv('CLICKHOUSE_PASSWORD')

# Create Kafka engine table for content table
CREATE_CONTENT_QUEUE_TABLE = '''
CREATE TABLE IF NOT EXISTS content_queue (
    `__op` String,
    `__ts_ms` UInt64,
    `__source` String,
    `__ts` String,
    `id` String,
    `slug` String,
    `title` String,
    `content_type` String,
    `length_seconds` Nullable(Int32),
    `publish_ts` String
) ENGINE = Kafka('redpanda-1:29092', 'pg.public.content', 'clickhouse_content_consumer_group')
SETTINGS kafka_format = 'JSONEachRow';
'''

# Create materialized view to process content data
CREATE_CONTENT_MV = '''
CREATE MATERIALIZED VIEW IF NOT EXISTS content_mv TO content AS
SELECT 
    `__op`,
    `__ts_ms`,
    `__source`,
    `__ts`,
    `id`,
    `slug`,
    `title`,
    `content_type`,
    `length_seconds`,
    `publish_ts`
FROM content_queue;
'''

# Create landing table for content
CREATE_CONTENT_LANDING_TABLE = '''
CREATE TABLE IF NOT EXISTS content (
    `__op` String,
    `__ts_ms` UInt64,
    `__source` String,
    `__ts` String,
    `id` String,
    `slug` String,
    `title` String,
    `content_type` String,
    `length_seconds` Nullable(Int32),
    `publish_ts` String
) ENGINE = MergeTree()
ORDER BY (`id`, `__ts_ms`);
'''

# Create Kafka engine table for engagement_events table
CREATE_ENGAGEMENT_EVENTS_QUEUE_TABLE = '''
CREATE TABLE IF NOT EXISTS engagement_events_queue (
    `__op` String,
    `__ts_ms` UInt64,
    `__source` String,
    `__ts` String,
    `id` String,
    `content_id` String,
    `user_id` String,
    `event_type` String,
    `event_ts` String,
    `duration_ms` Nullable(Int32),
    `device` String,
    `raw_payload` String
) ENGINE = Kafka('redpanda-1:29092', 'pg.public.engagement_events', 'clickhouse_engagement_consumer_group')
SETTINGS kafka_format = 'JSONEachRow';
'''

# Create materialized view to process engagement events data
CREATE_ENGAGEMENT_EVENTS_MV = '''
CREATE MATERIALIZED VIEW IF NOT EXISTS engagement_events_mv TO engagement_events AS
SELECT 
    `__op`,
    `__ts_ms`,
    `__source`,
    `__ts`,
    `id`,
    `content_id`,
    `user_id`,
    `event_type`,
    `event_ts`,
    `duration_ms`,
    `device`,
    `raw_payload`
FROM engagement_events_queue;
'''

# Create landing table for engagement events
CREATE_ENGAGEMENT_EVENTS_LANDING_TABLE = '''
CREATE TABLE IF NOT EXISTS engagement_events (
    `__op` String,
    `__ts_ms` UInt64,
    `__source` String,
    `__ts` String,
    `id` String,
    `content_id` String,
    `user_id` String,
    `event_type` String,
    `event_ts` String,
    `duration_ms` Nullable(Int32),
    `device` String,
    `raw_payload` String
) ENGINE = MergeTree()
ORDER BY (`id`, `__ts_ms`);
'''

def execute_all():
    try:
        # Connect to ClickHouse
        client = clickhouse_connect.get_client(
            host=CLICKHOUSE_HOST,
            port=int(CLICKHOUSE_PORT),
            user=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD
        )
        
        print("Connected to ClickHouse successfully!")
        
        # Create content tables
        print("Creating content tables...")
        client.command(CREATE_CONTENT_LANDING_TABLE)
        client.command(CREATE_CONTENT_QUEUE_TABLE)
        client.command(CREATE_CONTENT_MV)
        
        # Create engagement events tables
        print("Creating engagement events tables...")
        client.command(CREATE_ENGAGEMENT_EVENTS_LANDING_TABLE)
        client.command(CREATE_ENGAGEMENT_EVENTS_QUEUE_TABLE)
        client.command(CREATE_ENGAGEMENT_EVENTS_MV)
        
        print("All ClickHouse tables created successfully!")
        
        # Show created tables
        result = client.query("SHOW TABLES")
        print("\nCreated tables:")
        for row in result.result_rows:
            print(f"  - {row[0]}")
            
    except Exception as e:
        print(f"Error creating ClickHouse tables: {e}")
        raise
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    execute_all()
