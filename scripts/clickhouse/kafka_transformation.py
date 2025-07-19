import os
import json
import clickhouse_connect
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST')
CLICKHOUSE_PORT = os.getenv('CLICKHOUSE_HTTP_PORT')
CLICKHOUSE_USER = os.getenv('CLICKHOUSE_USER')
CLICKHOUSE_PASSWORD = os.getenv('CLICKHOUSE_PASSWORD')

# Create transformed table for joined data
CREATE_TRANSFORMED_TABLE = '''
CREATE TABLE IF NOT EXISTS content_engagement_transformed (
    engagement_id UInt64,
    user_id UUID,
    event_type String,
    event_ts String,
    duration_ms UInt32,
    device String,
    raw_payload String,
    content_type String,
    length_seconds UInt32,
    engagement_seconds UInt32,
    engagment_pct Float32,
    ingest_from_kafka_ts DateTime64(3),
    transform_ts DateTime64(3),
    ts_diff UInt64
) ENGINE = MergeTree()
ORDER BY (engagement_id);
'''

# Create materialized view for content transformations
CREATE_CONTENT_TRANSFORM_MV = '''
CREATE MATERIALIZED VIEW IF NOT EXISTS content_engagement_transformed_content_mv TO content_engagement_transformed AS
SELECT
    engagement_events.id as engagement_id,
    engagement_events.user_id as user_id,
    engagement_events.event_type as event_type,
    engagement_events.event_ts as event_ts,
    engagement_events.duration_ms as duration_ms,
    engagement_events.device as device,
    engagement_events.raw_payload as raw_payload,
    content.content_type as content_type,
    content.length_seconds as length_seconds,
    engagement_events.duration_ms / 1000 as engagement_seconds,
    ROUND(engagement_seconds / content.length_seconds, 2) as engagment_pct,
    engagement_events.ingest_from_kafka_ts as ingest_from_kafka_ts,
    now64(3) as transform_ts,
    (toUnixTimestamp64Milli(now64(3)) - toUnixTimestamp64Milli(engagement_events.ingest_from_kafka_ts)) / 1000 as ts_diff
FROM engagement_events
LEFT JOIN content ON engagement_events.content_id = content.id
'''

CREATE_CONTENT_TRANSFORM_QUEUE_MV = '''
CREATE MATERIALIZED VIEW IF NOT EXISTS content_engagement_transformed_queue_mv TO content_engagement_transformed_queue AS
SELECT
    engagement_id as _key,
    engagement_id,
    user_id,
    event_type,
    event_ts,
    duration_ms,
    device,
    raw_payload,
    content_type,
    length_seconds,
    engagement_seconds,
    engagment_pct,
    ingest_from_kafka_ts,
    transform_ts,
    ts_diff
FROM content_engagement_transformed
'''

CREATE_KAFKA_SOURCE_TABLE = '''
CREATE TABLE IF NOT EXISTS content_engagement_transformed_queue (
    _key String,
    engagement_id UInt64,
    user_id UUID,
    event_type String,
    event_ts String,
    duration_ms UInt32,
    device String,
    raw_payload String,
    content_type String,
    length_seconds UInt32,
    engagement_seconds UInt32,
    engagment_pct Float32,
    ingest_from_kafka_ts DateTime64(3),
    transform_ts DateTime64(3),
    ts_diff UInt64
) ENGINE = Kafka('redpanda-1:29092', 'ch.public.content_engagement_transformed', 'clickhouse_content_engagement_transformed_consumer_group')
SETTINGS kafka_format = 'JSONEachRow';
'''

def execute_all():
    client = clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=int(CLICKHOUSE_PORT),
        user=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD
    )
        
    print("Connected to ClickHouse successfully!")
    
    print("Creating transformed table...")
    client.command(CREATE_TRANSFORMED_TABLE)
    
    print("Creating content transformation materialized view...")
    client.command(CREATE_CONTENT_TRANSFORM_MV)
    
    print("Creating content transformation queue materialized view...")
    client.command(CREATE_CONTENT_TRANSFORM_QUEUE_MV)
    
    print("Creating Kafka source table...")
    client.command(CREATE_KAFKA_SOURCE_TABLE)
    
    print("All ClickHouse tables created successfully!")
        
if __name__ == "__main__":
    execute_all()
    execute_all()