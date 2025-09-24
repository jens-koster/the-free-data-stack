#!/bin/bash

echo "stopping jupyter service..."
freeds dc -s jupyter down

echo "building..."
freeds dc -s jupyter build
echo tagging freeds/jupyter-spark:latest
docker tag "freeds/jupyter-spark" "freeds/jupyter-spark:latest"

echo starting jupyter service...
freeds dc -s jupyter up
echo "all done"
