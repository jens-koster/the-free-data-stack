import json
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.docker_operator import DockerOperator
from docker.types import Mount

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def create_command(ds):
    p = {"execution_date": ds, "hours": 3}
    return f"--notebook wikipedia_pageviews_extract --parameters '{json.dumps(p)}'"


with DAG(
    "wikipedia_pageviews_extract",
    default_args=default_args,
    description="Run book_runner Docker container hourly",
    # schedule_interval='@hourly',
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:

    wikipedia_pageviews_extract = DockerOperator(
        task_id="wikipedia_pageviews_extract",
        image="tfds/papermill-base:1.0",
        command=create_command("{{ ds }}"),
        # docker_url='tcp://host.docker.internal:2375',
        # docker_url='tcp://host.docker.internal:2375','
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",

        mounts=[
            Mount(source="/tmp/notebooks", target="/tmp/notebooks", type="bind"),
            Mount(
                source="/tmp/output_notebooks",
                target="/tmp/output_notebooks",
                type="bind",
            ),
        ],
    )

    wikipedia_pageviews_extract
