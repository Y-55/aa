echo "Adding data to Postgres..."

# Define variables to hold the parsed values
N_CONTENT_PER_STEP=10
N_EVENTS_PER_STEP=200
N_PAUSE_TIME_SECONDS=2
SIMULATION_TIME_SECONDS=60

# Add data to Postgres
poetry run python scripts/postgres/simulate_data_ingestion.py $N_CONTENT_PER_STEP $N_EVENTS_PER_STEP $N_PAUSE_TIME_SECONDS $SIMULATION_TIME_SECONDS

echo "Done"