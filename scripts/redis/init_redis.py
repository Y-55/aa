import redis
import json
import time
from dotenv import load_dotenv
import os
load_dotenv()

def init_redis():
    """Initialize Redis with the content engagement index"""
    try:
        # Connect to Redis
        r = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=0, decode_responses=True)
        
        # Test connection
        r.ping()
        print("✅ Connected to Redis successfully")
        
        # Create the content engagement index
        index_command = [
            "FT.CREATE", "idx:content_engagement_time",
            "ON", "JSON",
            "PREFIX", "1", "ch.public.content_engagement_transformed:",
            "SCHEMA",
            "$.content_type", "AS", "content_type", "TAG", "SORTABLE",
            "$.event_type", "AS", "event_type", "TAG", "SORTABLE", 
            "$.event_ts", "AS", "event_ts", "TEXT", "SORTABLE",
            "$.engagement_seconds", "AS", "engagement_seconds", "NUMERIC", "SORTABLE",
            "$.duration_ms", "AS", "duration_ms", "NUMERIC", "SORTABLE"
        ]
        
        try:
            # Execute the index creation command
            result = r.execute_command(*index_command)
            print("✅ Content engagement index created successfully")
            print(f"Index creation result: {result}")
        except redis.exceptions.ResponseError as e:
            if "Index already exists" in str(e):
                print("ℹ️  Content engagement index already exists")
            else:
                print(f"❌ Error creating index: {e}")
                raise
        
        # List existing indexes to verify
        try:
            indexes = r.execute_command("FT._LIST")
            print(f"📋 Existing indexes: {indexes}")
        except redis.exceptions.ResponseError as e:
            print(f"⚠️  Could not list indexes: {e}")
        
        print("✅ Redis initialization completed")
        
    except redis.ConnectionError:
        print("❌ Failed to connect to Redis. Make sure Redis is running.")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise

if __name__ == "__main__":
    init_redis()
