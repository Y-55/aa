import redis
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

def connect_to_redis() -> redis.Redis:
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def execute_content_engagement_aggregation() -> List[Dict[str, Any]]:
    r = connect_to_redis()
    
    print("🔍 Starting Redis Search aggregation...")
    # Now execute the aggregation
    aggregation_command = [
        "FT.AGGREGATE", "idx:content_engagement_time", "*",
        "GROUPBY", "1", "@content_type",
        "REDUCE", "COUNT", "0", "AS", "total_events",
        "REDUCE", "SUM", "1", "@engagement_seconds", "AS", "total_engagement_seconds",
        "SORTBY", "2", "@total_engagement_seconds", "DESC"
    ]
    
    result = r.execute_command(*aggregation_command)
    
    print(f"✅ Aggregation completed successfully")
    print(f"📊 Raw Redis result: {result}")

if __name__ == "__main__":
    print("🚀 Executing Redis Search aggregation query...")
    execute_content_engagement_aggregation()
