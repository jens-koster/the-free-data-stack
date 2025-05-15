import json
import sys
import book_runner
import os
import docker
import papermill as pm

os.environ["AIRFLOW_CTX_EXECUTION_DATE"] = "2025-05-15T01:00:00+00:00"
os.environ["AIRFLOW_CTX_DAG_ID"] = 'Book_debugger_script'
os.environ["AIRFLOW_CTX_TASK_ID"] = 'bookrun'
os.environ["AIRFLOW_CTX_RUN_ID"] = f'manual__{os.environ["AIRFLOW_CTX_EXECUTION_DATE"]}'


def run_book_dev(notebook_name, notebook_prefix, params):
    os.environ['TFDS_CONFIG_URL'] = 'http://tfds-config:8005/api/configs'
    args = [
        'book_runner.py',
        '--notebook_name', notebook_name,
        '--notebook_prefix', notebook_prefix,
        '--parameters', json.dumps(params),
        '--kernel', '.venv'
    ]
    sys.argv = args
    book_runner.main()


def run_book_prod(notebook_name, notebook_prefix, params):

    client = docker.from_env()
    cmd = [
        'python3', 'book_runner.py',
        '--notebook_name', notebook_name,
        '--notebook_prefix', notebook_prefix,
        "--parameters", json.dumps(params)
    ]
    env_vars = {
        "AIRFLOW_CTX_EXECUTION_DATE": os.environ["AIRFLOW_CTX_EXECUTION_DATE"],
        "AIRFLOW_CTX_DAG_ID": os.environ["AIRFLOW_CTX_DAG_ID"],
        "AIRFLOW_CTX_TASK_ID": os.environ["AIRFLOW_CTX_TASK_ID"],
        "AIRFLOW_CTX_RUN_ID": os.environ["AIRFLOW_CTX_RUN_ID"]
    }

    container = client.containers.run(
        image="tfds/papermill-base:latest",
        command=cmd,
        auto_remove=True,
        network="tfds-network",
        environment=env_vars,
        tty=False, # for getting the logs, line by line rather tha char by char
        volumes={},
        detach=True  # for getting the logs at all
    )
    for line in container.logs(stream=True):
        print(line.decode().strip())

    container.wait()


def run_papermill(notebook_filename, params):
    """useful for debugging the notebook"""
    os.environ['TFDS_CONFIG_URL'] = 'http://tfds-config:8005/api/configs'
    book_runner.redirect_logging()
    tmp_dir = '/tmp/output_notebooks'
    os.makedirs(tmp_dir, exist_ok=True)
    pm.execute_notebook(
        input_path=notebook_filename,
        output_path=f'{tmp_dir}/output.ipynb',
        log_output=True,
        progress_bar=False,
        parameters=params,
    )


prefix = 'pipe-dreams/notebooks/wikipedia_pageviews'

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

params_hello = {
    "p1": 'book',
    "p2": "debugger"
}

nb = 'helloworld'
nb = '/Users/jens/src/pipe-dreams/notebooks/wikipedia_pageviews/wikipedia_pageviews_extract.ipynb'
nb = 'wikipedia_pageviews_extract'
nb = 'wikipedia_pageviews_bronze'
p = params_wiki_bronze

# run_papermill(notebook_filename=nb, params=p)
# run_book_dev(notebook_name=nb, notebook_prefix=prefix, params=p)
run_book_prod(notebook_name=nb, notebook_prefix=prefix, params=p)