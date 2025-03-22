#!/bin/bash

# GlossGen Deployment Check Script
echo "GlossGen Deployment Check Script"
echo "==============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed or not in PATH"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if the GlossGen container is running
CONTAINER_ID=$(docker ps -q --filter "name=glossgen")
if [ -z "$CONTAINER_ID" ]; then
    echo "Error: GlossGen container is not running"
    echo "Try starting it with: ./deploy-glossgen.sh"
    exit 1
else
    echo "✅ GlossGen container is running (ID: $CONTAINER_ID)"
fi

# Check if the port is accessible
if command -v curl &> /dev/null; then
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501)
    if [ "$HTTP_STATUS" -eq 200 ]; then
        echo "✅ GlossGen web interface is accessible at http://localhost:8501"
    else
        echo "⚠️ GlossGen web interface returned HTTP status $HTTP_STATUS"
    fi
else
    echo "⚠️ curl not found, cannot check web interface accessibility"
    echo "Please manually verify that http://localhost:8501 is accessible"
fi

# Check container logs for errors
ERROR_COUNT=$(docker logs $CONTAINER_ID 2>&1 | grep -i "error" | wc -l)
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "⚠️ Found $ERROR_COUNT error messages in container logs"
    echo "Check the logs with: docker logs $CONTAINER_ID"
else
    echo "✅ No errors found in container logs"
fi

echo ""
echo "Deployment check complete. If all checks passed, GlossGen is running correctly."
echo "Access the application at: http://localhost:8501" 