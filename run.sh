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

# Initialize the database with sample data
echo "Initializing database with sample data..."
python init_database.py

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