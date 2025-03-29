# globals
# a common folder for our lab data
ln -s "$(pwd)/_data" /tmp/data
# a folder where all logs are stores
mkdir -p /tmp/logs
# we need a common network so the containers can communicate
# this is apprently persistent so no need torun this command but once.
docker network create tfds-network

# Airflow
mkdir -p /tmp/logs/airflow
mkdir -p /tmp/airflow
ln -s "$(pwd)/Airflow/config" /tmp/airflow/config
ln -s "$(pwd)/Airflow/plugins" /tmp/airflow/plugins
ln -s "$(pwd)/Airflow/dags" /tmp/airflow/dags

