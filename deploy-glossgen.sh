#!/bin/bash

# GlossGen Deployment Script
echo "GlossGen Deployment Script"
echo "=========================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    if [ -f glossgen/.env.example ]; then
        cp glossgen/.env.example .env
        echo "Please edit the .env file with your configuration before continuing."
        exit 1
    else
        echo "Error: .env.example file not found!"
        exit 1
    fi
fi

# Build and start the Docker container
echo "Building and starting GlossGen container..."
docker-compose -f docker-compose.yml up -d --build

# Check if the container is running
if [ $? -eq 0 ]; then
    echo "GlossGen is now running!"
    echo "Access the application at http://localhost:8501"
else
    echo "Error: Failed to start GlossGen container."
    echo "Check the logs with: docker-compose -f docker-compose.yml logs"
    exit 1
fi 

