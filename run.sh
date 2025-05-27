#!/bin/bash

# Default mode
MODE=${1:-"app"}

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment and installing dependencies..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if test data exists, if not generate it
if [ ! -f "real_estate_agents/database/data/properties.json" ]; then
    echo "Generating test data..."
    python generate_test_data.py
else
    echo "Using existing test data..."
fi

if [ "$MODE" = "app" ]; then
    # Run the application
    echo "Starting the application..."
    python main.py
elif [ "$MODE" = "scraper" ]; then
    # Run the scraper scheduler
    echo "Starting the scraper scheduler..."
    python schedule_scraping.py
elif [ "$MODE" = "both" ]; then
    # Run both the application and the scraper scheduler
    echo "Starting both the application and the scraper scheduler..."
    python schedule_scraping.py &
    SCRAPER_PID=$!
    python main.py
    kill $SCRAPER_PID
else
    echo "Unknown mode: $MODE"
    echo "Usage: ./run.sh [app|scraper|both]"
    exit 1
fi