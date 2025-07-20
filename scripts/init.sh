echo "Initializing Postgres..."
poetry run python scripts/postgres/init_db.py

echo "Initializing Redpanda Postgres Connect..."
poetry run python scripts/redpanda/init_postgres_connect.py

echo "Initializing ClickHouse Landing Tables..."
poetry run python scripts/clickhouse/init_landing_tables.py

echo "Initializing ClickHouse Kafka Transformation..."
poetry run python scripts/clickhouse/kafka_transformation.py

echo "Initializing Redis Connect..."
poetry run python scripts/redpanda/init_redis_connect.py

echo "Initializing Redis..."
poetry run python scripts/redis/init_redis.py

echo "Running simulate..."
poetry run python scripts/postgres/simulate_data_ingestion.py 1 100 5 10

echo "Initializing Kafka Streams App..."
cd kafka_streams_app
nohup java -jar target/kafka_streams_app-1.0-SNAPSHOT.jar > /dev/null 2>&1 &
# java -jar target/kafka_streams_app-1.0-SNAPSHOT.jar

echo "Done"