#!/bin/bash

# filepath: /Users/jens/src/datastack/dc-wrapper.sh
export TFDS_VERSION=1.0
# Check if a Docker Compose command is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <docker-compose-command>"
    echo "Example: $0 up -d"
    exit 1
fi

# call all the stack items in order
# todo: reverse order for down and stop.
source ./dc.sh S3Ninja "$@"
source ./dc.sh tfds-config "$@"
source ./dc.sh PostgreSQL "$@"
source ./dc.sh Papermill "$@"
source ./dc.sh Spark "$@"
source ./dc.sh Airflow "$@"
