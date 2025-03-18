ln -s "$(pwd)/_data" /tmp/data

mkdir -p /tmp/logs/airflow
mkdir -p /tmp/airflow
mkdir -p /tmp/logs

mkdir -p /tmp/logs/notebook-runner
mkdir -p /tmp/notebooks
mkdir -p /tmp/output_notebooks



ln -s "$(pwd)/Airflow/config" /tmp/airflow/config
ln -s "$(pwd)/Airflow/plugins" /tmp/airflow/plugins
ln -s "$(pwd)/Airflow/dags" /tmp/airflow/dags

docker network create tfds-network
