#!/bin/bash

echo "clear all"
./scripts/clear.sh

echo "Running init.sh..."
./scripts/init.sh

echo "Running simulate..."
./scripts/simulate_data_ingestion.sh