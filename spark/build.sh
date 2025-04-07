#!/bin/bash

if [ -z "$1" ]; then
    echo "Error: No minor revision supplied. Please provide an int."
    return 1
fi


echo building
docker compose -f docker-compose-base.yml build

echo 'pushing...'

tag="tfds/spark-base:1.0"
echo "📦 pushing version $tag"
docker tag "spark-base" "$tag"
docker push "$tag"

tag="tfds/spark-base:1.0.$1"
echo "📦 pushing version $tag"
docker tag "spark-base" "$tag"
docker push "$tag"
