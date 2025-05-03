# Build and run a Docker container for the backend of the app

#!/bin/bash

# Variables
IMAGE_NAME="beautirag-backend"
CONTAINER_NAME="backend"
PORT=8000

# Stop and remove old container if it exists
echo "🔄 Removing old container (if exists)..."
docker rm -f $CONTAINER_NAME 2>/dev/null || true

# Build the Docker image
echo "🔨 Building image '$IMAGE_NAME'..."
docker build -t $IMAGE_NAME .

# Run the container
echo "🚀 Running container '$CONTAINER_NAME' on port $PORT..."
docker run -d -p $PORT:$PORT --name $CONTAINER_NAME $IMAGE_NAME

# Show running container
echo "✅ Container is running:"
docker ps | grep $CONTAINER_NAME
