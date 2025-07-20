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

echo "Done"