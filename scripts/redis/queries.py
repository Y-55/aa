import redis
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

load_dotenv()

REDIS_HOST = os.getenv('REDIS_CONNECT_HOST')
REDIS_PORT = os.getenv('REDIS_CONNECT_PORT')

def connect_to_redis() -> redis.Redis:
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def execute_content_engagement_aggregation() -> List[Dict[str, Any]]:
    r = connect_to_redis()
    try:
        result = r.execute_command(
            'FT.AGGREGATE',
            'idx:content_engagement_time',
            '*',
            'GROUPBY', '1', '@content_type',
            'REDUCE', 'COUNT', '0', 'AS', 'total_events',
            'REDUCE', 'SUM', '1', '@engagement_seconds', 'AS', 'total_engagement_seconds',
            'SORTBY', '2', '@total_engagement_seconds', 'DESC'
        )
        
        print(f"Raw Redis result: {result}")
        print(f"Result type: {type(result)}")
        print(f"Result length: {len(result)}")
        
        # parse the result
        parsed_result = []
        # Skip the first element (count) and process each group
        for i in range(1, len(result)):
            group_data = result[i]
            
            print(f"Processing group {i}: {group_data}")
            
            # Each group is a flat array with alternating key-value pairs
            content_type = None
            total_events = None
            total_engagement_seconds = None
            
            for j in range(0, len(group_data), 2):
                if j + 1 < len(group_data):
                    key = group_data[j]
                    value = group_data[j + 1]
                    
                    print(f"  Key: {key}, Value: {value}")
                    
                    if key == 'content_type':
                        content_type = value
                    elif key == 'total_events':
                        total_events = int(value)
                    elif key == 'total_engagement_seconds':
                        total_engagement_seconds = float(value)
            
            parsed_result.append({
                'content_type': content_type,
                'total_events': total_events,
                'total_engagement_seconds': total_engagement_seconds
            })
        
        return parsed_result
        
    except redis.exceptions.ResponseError as e:
        print(f"Redis error: {e}")
        return []
    except Exception as e:
        print(f"Error executing query: {e}")
        raise e
        return []

def main():
    print("Executing Redis Search aggregation query...")
    results = execute_content_engagement_aggregation()
    
    print("\nResults:")
    for i, item in enumerate(results):
        print(f"{i}: {item}")

if __name__ == "__main__":
    main()
