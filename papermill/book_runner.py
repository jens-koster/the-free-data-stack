"""
Run a notebook in papermill.
Intended as entrypoint to a docker container
some useful commands, full documentation in the readme.

set the env variables:
eval "$(python3 ./tfds_cli/tfds.py env | grep "^export TFDS_")"

run the debug version of the docker, where this file is mounted rather than deployed in the docker. (you can edit and run, no build)
docker compose run debug --notebook "pipe-dreams/notebooks/helloworld" --parameters '{"p1": "hello", "p2": "world"}'

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

def download_notebook(notebook, bucket, tmp_dir)->str:
    notebook_base_name = notebook.split('/')[-1]
    input_object_name = f"{notebook}.ipynb"
    input_local_filename = f"{tmp_dir}/{notebook_base_name}.ipynb"

    print(f"Downloading bucket: {bucket}, {input_object_name} to {input_local_filename}")
    try:
        s3_client = get_s3_client()
        s3_client.download_file(bucket, input_object_name, input_local_filename)
    except s3_client.exceptions.ClientError as e:
        print(f"Error downloading {notebook} from s3: {e.response['Error']['Message']}")
        return
    return input_local_filename


def make_output_filename(notebook):
    notebook_base_name = notebook.split('/')[-1]
    output_filename = f"{notebook_base_name}_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')}.ipynb"
    return output_filename


def redirect_logging():
        # Set up logging to print to both terminal and notebook

    logger = pm.log.logger
    logger.setLevel(logging.INFO)

    # Create a stream handler for terminal output
    terminal_handler = logging.StreamHandler(sys.stdout)
    terminal_handler.setLevel(logging.INFO)
    logger.addHandler(terminal_handler)



def execute_notebook(notebook, parameters, kernel):
    redirect_logging()
    notebook_prefix = '/'.join(notebook.split('/')[:-1])
    tmp_dir = f"/tmp/book_runner/{notebook_prefix}"
    os.makedirs(tmp_dir, exist_ok=True)

    input_local_filename = download_notebook(notebook, bucket="notebooks", tmp_dir=tmp_dir)

    print(f"Setting kernel to {kernel}")
    set_kernel (notebook_path=input_local_filename, kernel_name=kernel)

    output_filename = make_output_filename(notebook)
    output_local_filename = os.path.join(tmp_dir, output_filename)
    output_object_name = f"{notebook_prefix}/{output_filename}"

    print(f"Executing papermill: {input_local_filename} -> {output_local_filename}")
    pm.execute_notebook(
        input_path=input_local_filename,
        output_path=output_local_filename,
        log_output=True,
        progress_bar=False,
        parameters=parameters,
    )

    output_bucket = "output-notebooks"
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
        "--notebook",
        type=str,
        required=True,
        help="Notebok filename excluding the .ipynb extension",
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
    # Parse the parameters
    notebook = args.notebook
    print(f"Running notebook {notebook}")

    try:
        print(f"Parameters: {args.parameters}")
        parameters = json.loads(args.parameters)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON string for parameters")
    kernel = args.kernel
    execute_notebook(notebook=notebook, parameters=parameters, kernel=kernel)


if __name__ == '__main__':
    main()
