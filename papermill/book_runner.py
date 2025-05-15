"""
Run a notebook in papermill, intended to be run in a docker container by airflow.
Use book_debugger.py to run this script in dev mode.
"""

import argparse
import datetime as dt
import json
import logging
import os
import sys
import boto3
import papermill as pm
import requests
import nbformat

print("book_runner.py is running...")

def get_s3_config():

    tfds_config_url = os.environ.get("TFDS_CONFIG_URL")
    print(f"using tsdf-config: {tfds_config_url}")
    if not tfds_config_url:
        raise EnvironmentError("Environment variable TFDS_CONFIG_URL is not set")
    tfds_config_url += "/s3"
    print(f"retrieving s3 config from {tfds_config_url}")
    response = requests.get(tfds_config_url)
    response.raise_for_status()
    cfg = response.json().get("config")

    if cfg is None:
        raise ValueError(f"No config element found in response from config server: {response.text}")

    return cfg



def set_kernel(notebook_path, kernel_name):
    nb = nbformat.read(notebook_path, as_version=nbformat.NO_CONVERT)
    nb['metadata']['kernelspec']['name'] = kernel_name
    nbformat.write(nb, notebook_path)


def get_s3_client():
    cfg = get_s3_config()
    print(
        f"using s3 config url:{cfg['url']}, 'access_key': {'access_key' in cfg.keys()}, 'secret_key': {'secret_key' in cfg.keys()}"
    )

    s3_client = boto3.client(
        service_name="s3",
        aws_access_key_id=cfg["access_key"],
        aws_secret_access_key=cfg["secret_key"],
        endpoint_url=cfg["url"],
    )
    return s3_client

def download_notebook(notebook_name, notebook_prefix, bucket, tmp_dir)->str:

    source_object_name = f"{notebook_prefix}/{notebook_name}.ipynb"
    target_filename = f"{tmp_dir}/{notebook_name}.ipynb"

    print(f"Downloading {source_object_name} to {target_filename} from bucket {bucket}")
    try:
        s3_client = get_s3_client()
        s3_client.download_file(bucket, source_object_name, target_filename)
    except s3_client.exceptions.ClientError as e:
        print(f"Error downloading {source_object_name} from s3: {e.response['Error']['Message']}")
        return
    return target_filename

def redirect_logging():
    # Set up papermill logging to print output to both terminal and notebook
    logger = pm.log.logger
    logger.setLevel(logging.INFO)

    # Create a stream handler for terminal output
    terminal_handler = logging.StreamHandler(sys.stdout)
    terminal_handler.setLevel(logging.INFO)
    logger.addHandler(terminal_handler)



def execute_notebook(notebook_name:str, notebook_prefix:str, parameters:dict, kernel:str):
    """Execute a notebook: download the notebook from s3 and upload the result to s3.
    execution_date and execution_id are injected into parameters."""

    redirect_logging()
    tmp_dir = f"/tmp/book_runner/{notebook_prefix}"
    os.makedirs(tmp_dir, exist_ok=True)

    input_local_filename = download_notebook(
        notebook_name=notebook_name,
        notebook_prefix=notebook_prefix,
        bucket="notebooks",
        tmp_dir=tmp_dir)

    print(f"Setting kernel to {kernel}")
    set_kernel (notebook_path=input_local_filename, kernel_name=kernel)

    output_filename = f"{notebook_name}_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')}.ipynb"
    output_local_filename = os.path.join(tmp_dir, output_filename)
    output_object_name = f"{notebook_prefix}/{output_filename}"

    for key, value in os.environ.items():
        print(f"{key}={value}")
    parameters = parameters.copy()

    print(f"Executing papermill: {input_local_filename} -> {output_local_filename} with parameters: {parameters}")
    pm.execute_notebook(
        input_path=input_local_filename,
        output_path=output_local_filename,
        log_output=True,
        progress_bar=False,
        parameters=parameters,
    )

    output_bucket = "output-notebooks" # make this a config
    print(
        f"Uploading {output_local_filename} to bucket {output_bucket} as {output_object_name}"
    )
    s3_client = get_s3_client()
    with open(output_local_filename, "rb") as f:
        s3_client.upload_fileobj(f, output_bucket, output_object_name)

    print("Notebook executed")


def main():

    parser = argparse.ArgumentParser(
        description="Run a Jupyter notebook with papermill."
    )

    # notebook
    parser.add_argument(
        "--notebook_name",
        type=str,
        required=True,
        help="Notebok filename excluding the .ipynb extension",
    )
    parser.add_argument(
        "--notebook_prefix",
        type=str,
        required=True,
        help="s3 prefix for the notebook, e.g. pipe-dreams/notebooks",
    )
    # parameters
    parser.add_argument(
        "--parameters",
        type=str,
        required=True,
        help=(
            "JSON string of parameters to pass to the notebook, "
            "use doublequotes on value and key"
        ),
    )
    parser.add_argument(
        "--kernel",
        type=str,
        required=False,
        default="TFDS",
        help=(
            "Kernel for running the notebook. "
            "If not provided, 'TFDS' kernel is used."
        ),
    )

    args = parser.parse_args()
    if '/' in args.notebook_name:
        raise ValueError("Notebook name should not contain '/', prefix is provided in the notebook_prefix argument")
    print(f"Running notebook {args.notebook_prefix}/{args.notebook_name}")
    try:
        print(f"Parameters: {args.parameters}")
        parameters_dict = json.loads(args.parameters)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON string for parameters")

    execute_notebook(
        notebook_name=args.notebook_name,
        notebook_prefix=args.notebook_prefix,
        parameters=parameters_dict,
        kernel=args.kernel)


if __name__ == '__main__':
    main()
