import os
from datetime import datetime

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}


with DAG(
    dag_id="book_runner_dag",
    default_args=default_args,
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:
    print("-" * 50)
    print(os.environ.get("TFDS_CONFIG_URL"))
    print("-" * 50)
    run_book_runner = DockerOperator(
        task_id="run_book_runner",
        image="tfds/papermill-base:1.0.10",  # Use the same image as in docker-compose.yaml
        container_name=f"book_runner-{dag.dag_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        api_version="auto",
        force_pull=True,
        auto_remove="force",  # Automatically remove the container after execution
        command='--notebook helloworld --parameters \'{"p1":"hello", "p2":"world"}\'',
        docker_url="unix://var/run/docker.sock",  # Docker socket
        network_mode="tfds-network",  # Attach the container to the tfds-network
        mount_tmp_dir=False,
        environment={
            "TFDS_CONFIG_URL": os.environ.get("TFDS_CONFIG_URL"),
        },
    )

    run_book_runner
