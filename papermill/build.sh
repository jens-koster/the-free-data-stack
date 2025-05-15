#!/bin/bash

echo building ...
docker compose build
echo tagging tfds/paperpmill-base:latest
docker tag "papermill-base" "tfds/papermill-base:latest"
echo "all done"
