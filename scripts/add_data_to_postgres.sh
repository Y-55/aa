echo "Adding data to Postgres..."

# Define variables to hold the parsed values
N_ADDED_ROWS_PER_STEP=1000
N_SIM_TIME_SECONDS=10
N_PAUSE_TIME_SECONDS=10

# Add data to Postgres
python scripts/postgres/add_data.py $N_ADDED_ROWS_PER_STEP $N_SIM_TIME_SECONDS $N_PAUSE_TIME_SECONDS

echo "Done"