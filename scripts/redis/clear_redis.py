import redis
import os
from dotenv import load_dotenv

load_dotenv()

def clear_redis():
    """Clear all data from Redis using FLUSHALL command"""
    
    # Get Redis connection details from environment or use defaults
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = int(os.getenv('REDIS_PORT'))
    
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.ping()
        
        result = r.flushall()
        
        if result:
            print("✅ Successfully cleared Redis")
        else:
            print("❌ Failed to clear Redis")
            
    except redis.exceptions.ConnectionError as e:
        print(f"❌ Failed to connect to Redis: {e}")
        return False
    except redis.exceptions.ResponseError as e:
        print(f"❌ Redis error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def main():
    clear_redis()

if __name__ == "__main__":
    main()
