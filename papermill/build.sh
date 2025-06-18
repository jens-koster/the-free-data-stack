#!/bin/bash

echo building ...
freeds dc -s . build
echo tagging tfds/paperpmill-base:latest
docker tag "papermill-base" "tfds/papermill-base:latest"
echo "all done"
