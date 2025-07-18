echo "Clearing Redpanda Postgres Connect..."
poetry run python scripts/redpanda/clear_connectors.py

echo "Clearing Postgres DB..."
poetry run python scripts/postgres/clear_db.py

echo "Clearing Redpanda Topics..."
poetry run python scripts/redpanda/clear_topics.py

echo "Done"
