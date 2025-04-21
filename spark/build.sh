#!/bin/bash
set -e
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

echo "re-installing spark requirements for this venv"
pip uninstall -r requirements.txt -y
pip install -r requirements.txt


MINOR_VERSION="$1"
FILE="docker-compose.yml"

echo "updating docker compsoe file"
# Use sed to update all occurrences of 1.0.x to 1.0.<new version>
sed -i.bak -E "s/1\.0\.[0-9]+/1.0.$MINOR_VERSION/g" "$FILE"
echo "Updated docker-compose.yml to use version 1.0.$MINOR_VERSION"
echo "restarting cluster"
docker compose down
docker compose up -d --remove-orphans
