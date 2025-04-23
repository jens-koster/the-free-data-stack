#!/bin/bash
echo "\n=============================================="
echo "| building the spark cluster                 |"
echo "==============================================\n"


echo "🔄 Auto incrementing version number..."

IMAGE_PREFIX="tfds/spark-base:1.0."
FILE="docker-compose.yml"

# Extract the current version number
current_version=$(grep -oE "${IMAGE_PREFIX}[0-9]+" "$FILE" | sed "s|${IMAGE_PREFIX}||" | head -n 1)

if [[ -z "$current_version" ]]; then
  echo "❌ Could not find a version like ${IMAGE_PREFIX}x in $FILE"
  exit 1
fi

# Increment version
new_version=$((current_version + 1))

# Replace in the file using '|' as delimiter
sed -i.bak "s|${IMAGE_PREFIX}${current_version}|${IMAGE_PREFIX}${new_version}|g" "$FILE"

echo "✅ Updated docker image in $FILE: ${IMAGE_PREFIX}${current_version} → ${IMAGE_PREFIX}${new_version}"

echo "downloading jar packages to package_jars"
rm -rf package_jars
mkdir -p package_jars
coursier fetch \
    io.delta:delta-spark_2.12:3.3.0 \
    org.apache.hadoop:hadoop-aws:3.3.4 \
    org.apache.hadoop:hadoop-common:3.3.4 \
    com.amazonaws:aws-java-sdk-bundle:1.12.262 \
    --classpath | tr ':' '\n' | while read jar; do cp "$jar" package_jars/; done

rm -rf docker_jars
echo "copying spark jars from apache image"
docker create --name spark-temp apache/spark:3.5.5
docker cp spark-temp:/opt/spark/jars ./docker_jars
docker rm spark-temp

python3 fix_jars.py

echo building docker image
docker compose -f docker-compose-base.yml build

echo 'pushing...'

tag="tfds/spark-base:1.0"
echo "📦 pushing version $tag"
docker tag "spark-base" "$tag"
docker push "$tag"

tag="tfds/spark-base:1.0.$new_version"
echo "📦 pushing version $tag"
docker tag "spark-base" "$tag"
docker push "$tag"

echo "re-installing spark requirements for this venv"
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

echo "merging docker_jars and package_jars to jars folder"
mkdir -p jars
cp docker_jars/*.jar jars/
cp package_jars/*.jar jars/
rm -rf package_jars docker_jars

echo "restarting cluster"
docker compose down
docker compose up -d --remove-orphans

docker ps

echo "Make sure spark is: 1.0.$new_version"