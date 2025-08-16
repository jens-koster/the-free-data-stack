#!/bin/bash
if [[ -z "$VIRTUAL_ENV" ]]; then
  echo "❌ No virtual environment is activated. Please activate a venv and try again."
  return
fi

echo "\n=============================================="
echo "| building the spark cluster                 |"
echo "==============================================\n"

echo "stopping cluster"
docker compose down

echo "re-installing spark requirements for this venv"
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

source jar.sh

echo building docker image
freeds dc -s . build

echo 'tagging docker image "freeds/spark-base:latest"'
docker tag "freeds/spark-base" "freeds/spark-base:latest"

echo "merging docker_jars and package_jars to jars folder"
mkdir -p jars
cp docker_jars/*.jar jars/
cp package_jars/*.jar jars/


echo "starting cluster"
freeds docker compose up -d --remove-orphans

echo "building papermill"

cd ../jupyter
source build.sh
cd ../spark
