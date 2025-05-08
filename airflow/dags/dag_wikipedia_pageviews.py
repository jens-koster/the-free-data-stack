import json
from datetime import datetime, timedelta

from airflow.decorators import dag, task
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

    def build_command(execution_date: str):
        params = {
            "execution_hour_str": execution_date,
            "output_bucket": "data",
            "output_root_prefix": "wikipedia_pageviews",
            "overlap_hours": 1,
            "force_reupload": False,
        }
        return f"--notebook pipe-dreams/notebooks/wikipedia_pageviews/wikipedia_pageviews_extract --parameters '{json.dumps(params)}'"

    extract_task = DockerOperator(
        task_id="extract",
        image="tfds/papermill-base:1.0.21",
        force_pull=True,
        command=build_command("{{ ds }}"),
        auto_remove='force',
        docker_url="unix://var/run/docker.sock",
        network_mode="tfds-network",
        mount_tmp_dir=False,
    )

    extract_task


dag = extract_wikipedia_pageviews_dag()
