#!/bin/bash

# Build and run the Docker containers
docker-compose up --build -d

echo "Real Estate Multi-Agent System is running!"
echo "Web interface: http://localhost:8000"
echo "API: http://localhost:8000/docs"
echo ""
echo "To stop the system, run: docker-compose down"