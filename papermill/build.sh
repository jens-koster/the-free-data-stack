#!/bin/bash
if [ -z "$1" ]; then
    echo "Error: No minor revision supplied. Please provide an int."
    return 1
fi
docker login

docker compose build

echo 'pushing...'
docker tag "papermill-base" "tfds/papermill-base:1.0"
docker push "tfds/$1-base:1.0"

docker tag "papermill-base" "tfds/papermill-base:1.0.$1"
docker push "tfds/papermill-base:1.0.$1"
