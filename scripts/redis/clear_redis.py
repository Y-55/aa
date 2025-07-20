import redis
import os
from dotenv import load_dotenv

load_dotenv()

def clear_redis():
    """Clear all data from Redis using FLUSHALL command and drop indexes"""
    
    # Get Redis connection details from environment or use defaults
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = int(os.getenv('REDIS_PORT'))
    
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.ping()
        
        # Drop the content engagement index if it exists
        try:
            r.execute_command("FT.DROPINDEX", "idx:content_engagement_time")
            print("✅ Successfully dropped content engagement index")
        except redis.exceptions.ResponseError as e:
            if "Unknown index name" in str(e):
                print("ℹ️  Content engagement index does not exist (already dropped)")
            else:
                print(f"⚠️  Error dropping index: {e}")
        
        # Clear all data
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
