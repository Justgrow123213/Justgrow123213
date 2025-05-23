#!/bin/bash

# Initialize the database with sample data
echo "Initializing database with sample data..."
python init_database.py

# Run the application
echo "Starting the application..."
python main.py