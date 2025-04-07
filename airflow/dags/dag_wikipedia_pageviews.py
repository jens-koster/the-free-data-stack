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
    "retries": 2,
    "retry_delay": timedelta(minutes=5),

}


def create_command(ds):

    p = {
        "execution_hour_str": ds,
        "output_bucket": "data",
        "output_root_prefix": "wikipedia_pageviews",
        "overlap_hours": 25,
        "force_reupload": False
    }
    return f"--notebook pipe-dreams/notebooks/extract_wikipedia_pageviews --parameters '{json.dumps(p)}'"


with DAG(
    "extract_wikipedia_pageviews",
    default_args=default_args,
    description="Download wikipedia pageviews hourly",
    schedule_interval='@daily',
    start_date=datetime(2025, 1, 1),
    end_date = None,
    catchup=True,
    max_active_runs=1,
) as dag:

    wikipedia_pageviews_extract = DockerOperator(
        task_id="extract",
        image="tfds/papermill-base:1.0.21",
        force_pull=True,
        command=create_command("{{ ds }}"),
        auto_remove='force',
        docker_url="unix://var/run/docker.sock",
        network_mode="tfds-network",  # Attach the container to the tfds-network
        mount_tmp_dir=False

    )

    wikipedia_pageviews_extract
