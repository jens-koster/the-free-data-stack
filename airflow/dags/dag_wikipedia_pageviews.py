import json
from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.operators.docker_operator import DockerOperator


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=5),
}

IMAGE = "tfds/papermill-base:latest"
DOCKER_URL = "unix://var/run/docker.sock"
NETWORK_MODE = "tfds-network"
NOTEBOOK_DIR = "pipe-dreams/notebooks/wikipedia_pageviews"

def build_command(notebook_name: str, execution_date: str) -> str:
    params = {
        "execution_hour_str": execution_date,
        "output_bucket": "data",
        "output_root_prefix": "wikipedia_pageviews",
        "overlap_hours": 1,
        "force_reupload": False,
    }
    return f"--notebook {NOTEBOOK_DIR}/{notebook_name} --parameters '{json.dumps(params)}'"


@dag(
    dag_id="extract_wikipedia_pageviews",
    default_args=default_args,
    description="Download wikipedia pageviews hourly",
    schedule_interval="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=True,
    max_active_runs=1,
    tags=["wikipedia", "pageviews"],
)
def extract_wikipedia_pageviews_dag():
    extract = DockerOperator(
        task_id="extract",
        image=IMAGE,
        command=build_command("wikipedia_pageviews_extract", "{{ ds }}"),
        auto_remove="force",
        docker_url=DOCKER_URL,
        network_mode=NETWORK_MODE,
        mount_tmp_dir=False,
    )

    bronze = DockerOperator(
        task_id="bronze",
        image=IMAGE,
        command=build_command("wikipedia_pageviews_bronze", "{{ ds }}"),
        auto_remove="force",
        docker_url=DOCKER_URL,
        network_mode=NETWORK_MODE,
        mount_tmp_dir=False,
    )

    silver = DockerOperator(
        task_id="silver",
        image=IMAGE,
        command=build_command("wikipedia_pageviews_silver", "{{ ds }}"),
        auto_remove="force",
        docker_url=DOCKER_URL,
        network_mode=NETWORK_MODE,
        mount_tmp_dir=False,
    )

    extract >> bronze >> silver


dag = extract_wikipedia_pageviews_dag()
