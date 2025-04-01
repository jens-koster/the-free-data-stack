"""
Run a notebook in papermill.
Intended as entrypoint to a docker container
some useful commands, full documentation in the readme.
python3 book_runner.py --notebook helloworld --parameters '{"p1":"hello", "p2":"world"}'
docker compose run book-runner --notebook 'helloworld' --parameters '{"p1":"hello", "p2":"world"}'
docker compose run --remove-orphans --rm -it --entrypoint /bin/bash book-runner

"""

import argparse
import datetime as dt
import json
import os

import boto3
import papermill as pm
import requests

# we temorarily use the scrape keys function to get the keys for s3 ninja



print("book_runner.py is running...")

def get_s3_config():

    tfds_config_url = os.environ.get("TFDS_CONFIG_URL")
    print(f"using tsdf-config: {tfds_config_url}")
    if not tfds_config_url:
        raise EnvironmentError("Environment variable TFDS_CONFIG_URL is not set")
    tfds_config_url += "/s3"
    if os.environ.get("TFSD_CONFIG_LOCALHOST"):
        tfds_config_url += "?localhost=yes"
    print(f"retrieving s3 config from {tfds_config_url}")
    response = requests.get(tfds_config_url)

    return response.json()["config"]


def execute_notebook(notebook, parameters):
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

    tmp_dir = f"/tmp/book_runner/{notebook}"
    os.makedirs(tmp_dir, exist_ok=True)

    input_bucket = "notebooks"
    input_object_name = f"{notebook}.ipynb"
    input_local_file = f"{tmp_dir}/{notebook}.ipynb"

    output_bucket = "output-notebooks"
    output_prefix = f"{notebook}"
    output_filename = (
        f"{notebook}_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')}.ipynb"
    )

    output_object_name = f"{output_prefix}/{output_filename}"
    output_local_file = f"{tmp_dir}/{output_filename}"

    print(f"Downloading {input_bucket}, {input_object_name} to {input_local_file}")
    try:
        s3_client.download_file(input_bucket, input_object_name, input_local_file)
    except s3_client.exceptions.ClientError as e:
        print(f"Error downloading {notebook} from s3: {e.response['Error']['Message']}")
        return

    print(f"Executing papermill: {input_local_file} -> {output_local_file}")
    pm.execute_notebook(
        input_path=input_local_file,
        output_path=output_local_file,
        parameters=parameters,
    )

    print(
        f"Uploading {output_local_file} to bucket {output_bucket} as {output_object_name}"
    )
    with open(output_local_file, "rb") as f:
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

    args = parser.parse_args()
    # Parse the parameters
    notebook = args.notebook
    print(f"Running notebook {notebook}")

    try:
        print(f"Parameters: {args.parameters}")
        parameters = json.loads(args.parameters)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON string for parameters")

    execute_notebook(notebook=notebook, parameters=parameters)


if __name__ == '__main__':
    main()
