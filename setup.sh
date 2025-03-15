ln -s "$(pwd)/_data" /tmp/data
ln -s "$(pwd)/airflow" /tmp/airflow
docker network create tfds-network
