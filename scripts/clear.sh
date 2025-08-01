echo "Clearing Redpanda Postgres Connect..."
poetry run python scripts/redpanda/clear_debezium_connectors.py

echo "Clearing Redis Connectors..."
poetry run python scripts/redpanda/clear_redis_connectors.py

echo "Clearing Postgres DB..."
poetry run python scripts/postgres/clear_db.py

echo "Clearing Redpanda Topics..."
poetry run python scripts/redpanda/clear_topics.py

echo "Clearing ClickHouse DB..."
poetry run python scripts/clickhouse/clear_db.py

echo "Clearing Redis..."
poetry run python scripts/redis/clear_redis.py

echo "Clearing Kafka Streams App..."
PID=$(ps aux | grep "com.thmanyah.App" | grep -v grep | awk '{print $2}')
if [ -n "$PID" ]; then
    kill $PID
    kill -9 $PID
fi

echo "Done"
