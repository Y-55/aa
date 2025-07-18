echo "Adding data to Postgres..."

# Define variables to hold the parsed values
N_CONTENT_PER_STEP=5
N_EVENTS_PER_STEP=1000
N_PAUSE_TIME_SECONDS=5
SIMULATION_TIME_SECONDS=20

# Add data to Postgres
python scripts/postgres/simulate_data_ingestion.py $N_CONTENT_PER_STEP $N_EVENTS_PER_STEP $N_PAUSE_TIME_SECONDS $SIMULATION_TIME_SECONDS

echo "Done"