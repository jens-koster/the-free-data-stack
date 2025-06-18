import datetime as dt
import json
import logging
import os
import sys
from typing import Any

import book_runner
import docker

import papermill as pm

logging.basicConfig(level=logging.INFO)


def run_book_dev(notebook_name: str, notebook_prefix: str, params: str) -> None:
    os.environ["TFDS_CONFIG_URL"] = "http://tfds-config:8005/api/configs"
    args = [
        "book_runner.py",
        "--notebook_name",
        notebook_name,
        "--notebook_prefix",
        notebook_prefix,
        "--parameters",
        json.dumps(params),
        "--kernel",
        ".venv",
    ]
    sys.argv = args
    book_runner.main()


def run_book(notebook_name: str, notebook_prefix: str, params: dict[str, Any]) -> Any:
    """Run a notebook in a docker container using papermill.
    injecting the execution date and an execution id into the notebook params.
    """
    print(f"Initiating run of {notebook_prefix}/{notebook_name} with params: {params}")

    params = params.copy()

    hourly = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
    params["execution_date"] = hourly.isoformat()
    params["execution_id"] = "book_debugger"

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
        "TFDS_CONFIG_URL": "http://tfds-config:8005/api/configs",
    }
    client = docker.from_env()
    try:
        container = client.containers.run(
            image="freeds/jupyter-spark:latest",
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


def run_papermill(notebook_filename: str, params: dict[str, Any]) -> None:
    """Run straight in papermill, useful for debugging the notebook."""
    os.environ["TFDS_CONFIG_URL"] = "http://tfds-config:8005/api/configs"
    book_runner.redirect_logging()
    tmp_dir = "/tmp/output_notebooks"
    os.makedirs(tmp_dir, exist_ok=True)
    pm.execute_notebook(  # type: ignore[attr-defined]
        input_path=notebook_filename,
        output_path=f"{tmp_dir}/output.ipynb",
        log_output=True,
        progress_bar=False,
        parameters=params,
    )


params_wiki_extract = {
    "output_bucket": "data",
    "output_root_prefix": "wikipedia_pageviews",
    "overlap_hours": 1,
    "force_reupload": False,
}

params_wiki_bronze = {
    "bronze_db": "bronze",
}
params_wiki_silver = {
    "bronze_db": "bronze",
    "silver_db": "silver",
}

params_hello = {"p1": "book", "p2": "debugger"}

nb = "wikipedia_pageviews_bronze"
nb = "helloworld"
nb = "/Users/jens/src/pipe-dreams/notebooks/wikipedia_pageviews/wikipedia_pageviews_extract.ipynb"
nb = "wikipedia_pageviews_extract"
p = params_wiki_extract
prefix = "pipe-dreams/notebooks/wikipedia_pageviews"

# run_papermill(notebook_filename=nb, params=p)

run_book(notebook_name=nb, notebook_prefix=prefix, params=p)
# run_book(notebook_name=nb, notebook_prefix="pipe-dreams/notebooks", params=p)
