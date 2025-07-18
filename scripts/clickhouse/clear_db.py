import os
import clickhouse_connect
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('CLICKHOUSE_HOST')
DB_PORT = os.getenv('CLICKHOUSE_PORT')
DB_NAME = os.getenv('CLICKHOUSE_DB')
DB_USER = os.getenv('CLICKHOUSE_USER')
DB_PASSWORD = os.getenv('CLICKHOUSE_PASSWORD')

def clear_db():
    # Connect to ClickHouse
    client = clickhouse_connect.get_client(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        username=DB_USER,
        password=DB_PASSWORD
    )
    
    try:
        # Get all tables in the default database
        result = client.query("SHOW TABLES FROM default")
        tables = [row[0] for row in result.result_rows]
        
        print(f"Found {len(tables)} tables in default database")
        
        # Drop each table
        for table in tables:
            print(f"Dropping table: {table}")
            client.command(f"DROP TABLE IF EXISTS default.{table}")
            
        print("All tables in default database have been cleared")
        
    except Exception as e:
        print(f"Error clearing database: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    clear_db()
