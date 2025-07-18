echo "Clearing Redpanda Postgres Connect..."
poetry run python scripts/redpanda/clear_connectors.py

echo "Clearing Postgres DB..."
poetry run python scripts/postgres/clear_db.py

echo "Done"
