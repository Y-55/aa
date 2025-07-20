echo "Adding data to Postgres..."

# Define variables to hold the parsed values
N_CONTENT_PER_STEP=1
N_EVENTS_PER_STEP=100
N_PAUSE_TIME_SECONDS=5
SIMULATION_TIME_SECONDS=100

# Add data to Postgres
poetry run python scripts/postgres/simulate_data_ingestion.py $N_CONTENT_PER_STEP $N_EVENTS_PER_STEP $N_PAUSE_TIME_SECONDS $SIMULATION_TIME_SECONDS

echo "Done"