echo "Initializing Postgres..."
poetry run python scripts/postgres/init_db.py

echo "Initializing Redpanda Postgres Connect..."
poetry run python scripts/redpanda/init_postgres_connect.py

echo "Done"