#!/bin/bash
if [[ -z "$VIRTUAL_ENV" ]]; then
  echo "❌ No virtual environment is activated. Please activate a venv and try again."
  return
fi

echo "\n=============================================="
echo "| building the spark cluster                 |"
echo "==============================================\n"

echo "stopping cluster"
freeds dc -s spark down

source jar.sh

echo building docker image
freeds dc -s spark build

echo 'tagging docker image "freeds/spark-base:latest"'
docker tag "freeds/spark-base" "freeds/spark-base:latest"

echo "merging docker_jars and package_jars to jars folder"
mkdir -p jars
cp docker_jars/*.jar jars/
cp package_jars/*.jar jars/

echo "starting cluster"
freeds dc -s spark up --remove-orphans

echo "building jupyter"

cd ../jupyter
source build.sh
cd ../spark
