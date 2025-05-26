import datetime as dt
import json
import os

import docker
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context

default_args = {
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
}

# DOCKER_URL = "unix://var/run/docker.sock"


def create_execution_id(notebook_name, notebook_prefix, context):
    """Build a unique string to represent this notebook execution in logging and as spark app name etc."""
    dag_id = context["dag"].dag_id
    task_id = context["task"].task_id
    run_id = context["run_id"]
    return f"{dag_id}__{task_id}__{run_id}"


def run_book(notebook_name: str, notebook_prefix: str, params: dict, context: dict):
    """Run a notebook in a docker container using papermill.
    injecting the execution date and an execution id into the notebook params.
    """
    print(f"Initiating run of {notebook_prefix}/{notebook_name} with params: {params}")

    params = params.copy()

    if context.get("execution_date"):
        params["execution_date"] = context["execution_date"].isoformat()
    else:
        hourly = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
        params["execution_date"] = hourly.isoformat()

    params["execution_id"] = create_execution_id(
        notebook_name=notebook_name, notebook_prefix=notebook_prefix, context=context
    )

    cmd = [
        "python3",
        "book_runner.py",
        "--notebook_name",
        notebook_name,
        "--notebook_prefix",
        notebook_prefix,
        "--parameters",
        json.dumps(params),
    ]

    env_vars = {
        "TFDS_CONFIG_URL": os.environ.get("TFDS_CONFIG_URL", ""),
    }
    client = docker.from_env()
    try:
        container = client.containers.run(
            image="tfds/papermill-base:latest",
            command=cmd,
            auto_remove=True,
            network="tfds-network",
            environment=env_vars,
            tty=False,  # for getting the logs, line by line rather tha char by char
            detach=True,  # for getting the logs at all
        )
        for line in container.logs(stream=True):
            print(line.decode().strip())
        result = container.wait()
        if result.get("StatusCode", 1) != 0:
            raise RuntimeError(f"Notebook container exited with code {result['StatusCode']}")
        return result

    except docker.errors.DockerException as e:
        print(f"Docker error: {e}")
        raise
    finally:
        client.close()


@task
def extract_task():
    notebook_params = {
        "output_bucket": "data",
        "output_root_prefix": "wikipedia_pageviews",
        "overlap_hours": 8,
        "force_reupload": False,
    }
    notebook_prefix = "pipe-dreams/notebooks/wikipedia_pageviews"
    notebook_name = "wikipedia_pageviews_extract"
    run_book(
        notebook_name=notebook_name,
        notebook_prefix=notebook_prefix,
        params=notebook_params,
        context=get_current_context(),
    )


@task
def bronze_task():
    notebook_params = {"bronze_db": "bronze"}
    notebook_prefix = "pipe-dreams/notebooks/wikipedia_pageviews"
    notebook_name = "wikipedia_pageviews_bronze"
    run_book(
        notebook_name=notebook_name,
        notebook_prefix=notebook_prefix,
        params=notebook_params,
        context=get_current_context(),
    )


@task
def silver_task():
    notebook_params = {"bronze_db": "bronze", "silver_db": "silver"}
    notebook_prefix = "pipe-dreams/notebooks/wikipedia_pageviews"
    notebook_name = "wikipedia_pageviews_silver"
    run_book(
        notebook_name=notebook_name,
        notebook_prefix=notebook_prefix,
        params=notebook_params,
        context=get_current_context(),
    )


@dag(
    dag_id="wikipedia_pageview_pipeline",
    default_args=default_args,
    description="Download and process wikipedia pageviews hourly",
    schedule_interval="@hourly",
    start_date=dt.datetime(2025, 1, 1),
    catchup=True,
    max_active_runs=1,
    tags=["wikipedia", "pageviews"],
)
def wikipedia_pageviews_dag():

    extract = extract_task()
    bronze = bronze_task()
    silver = silver_task()

    extract >> bronze >> silver


dag = wikipedia_pageviews_dag()
