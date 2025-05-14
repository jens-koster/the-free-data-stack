#!/bin/bash

echo building perpmill-base:latest
docker compose build

docker tag "papermill-base" "tfds/papermill-base:latest"
