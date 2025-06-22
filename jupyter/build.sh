#!/bin/bash

echo building ...
freeds dc -s jupyter build
echo tagging freeds/jupyter-spark:latest
docker tag "freeds/jupyter-spark" "freeds/jupyter-spark:latest"
echo "all done"
