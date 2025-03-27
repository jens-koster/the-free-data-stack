#!/bin/bash

# filepath: /Users/jens/src/datastack/dc.sh

# Check if a folder name is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <folder-name> <docker-compose-command>"
    echo "Example: $0 s3-ninja up -d"
    exit 1
fi

# Save the folder name and shift the arguments
TARGET_DIR="$1"
shift

# Check if a Docker Compose command is provided
if [ -z "$1" ]; then
    echo "Error: No Docker Compose command provided."
    echo "Example: $0 s3-ninja up -d"
    exit 1
fi

# Save the current directory
START_DIR=$(pwd)

# Navigate to the target folder
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' does not exist."
    exit 1
fi

cd "$TARGET_DIR" || { echo "Failed to change directory to $TARGET_DIR"; exit 1; }

# Execute the Docker Compose command
echo "Running 'docker compose $*' in $(pwd)"
docker compose "$@"

# Return to the original directory
cd "$START_DIR" || { echo "Failed to return to the original directory"; exit 1; }

echo "Returned to $START_DIR"
