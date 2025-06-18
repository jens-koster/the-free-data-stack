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

echo "🔄 Auto incrementing version number..."

# IMAGE_PREFIX="freeds/spark-base:1.0."
# FILE="docker-compose.yaml"

# # Extract the current version number
# current_version=$(grep -oE "${IMAGE_PREFIX}[0-9]+" "$FILE" | sed "s|${IMAGE_PREFIX}||" | head -n 1)

# if [[ -z "$current_version" ]]; then
#   echo "❌ Could not find a version like ${IMAGE_PREFIX}x in $FILE"
#   exit 1
# fi

# # Increment version
# new_version=$((current_version + 1))

# # Replace in the file using '|' as delimiter
# sed -i.bak "s|${IMAGE_PREFIX}${current_version}|${IMAGE_PREFIX}${new_version}|g" "$FILE"
# echo "✅ Updated docker image in $FILE: ${IMAGE_PREFIX}${current_version} → ${IMAGE_PREFIX}${new_version}"

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

cd ../papermill
source build.sh
cd ../spark
