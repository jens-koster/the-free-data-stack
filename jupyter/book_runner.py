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
from typing import Any

import nbformat
import papermill as pm
from freeds.s3 import get_file, put_file
from freeds.utils import setup_logging

print("book_runner.py is running...")
setup_logging(__name__)


def set_kernel(notebook_path: str, kernel_name: str) -> None:
    print(f"Setting kernel to {kernel_name}")
    nb = nbformat.read(notebook_path, as_version=nbformat.NO_CONVERT)
    nb["metadata"]["kernelspec"]["name"] = kernel_name
    nbformat.write(nb, notebook_path)


def download_notebook(notebook_name: str, notebook_prefix: str, bucket: str, tmp_dir: str) -> str:

    source_object_name = f"{notebook_prefix}/{notebook_name}.ipynb"
    target_filename = f"{tmp_dir}/{notebook_name}.ipynb"

    print(f"Downloading {source_object_name} to {target_filename} from bucket {bucket}")
    get_file(local_path=target_filename, bucket=bucket, file_name=source_object_name)
    return target_filename


def redirect_logging() -> None:
    # Set up papermill logging to print output to both terminal and notebook
    logger = pm.log.logger
    logger.setLevel(logging.INFO)

    # Create a stream handler for terminal output
    terminal_handler = logging.StreamHandler(sys.stdout)
    terminal_handler.setLevel(logging.INFO)
    logger.addHandler(terminal_handler)


def execute_notebook(notebook_name: str, notebook_prefix: str, parameters: dict[str, Any], kernel: str) -> None:
    """Execute a notebook: download the notebook from s3 and upload the result to s3.
    execution_date and execution_id are injected into parameters."""

    redirect_logging()
    tmp_dir = f"/tmp/book_runner/{notebook_prefix}"
    os.makedirs(tmp_dir, exist_ok=True)

    input_local_filename = download_notebook(
        notebook_name=notebook_name, notebook_prefix=notebook_prefix, bucket="notebooks", tmp_dir=tmp_dir
    )

    set_kernel(notebook_path=input_local_filename, kernel_name=kernel)

    output_filename = f"{notebook_name}_{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')}.ipynb"
    output_local_filename = os.path.join(tmp_dir, output_filename)
    output_object_name = f"{notebook_prefix}/{output_filename}"

    parameters = parameters.copy()

    print(f"Executing papermill: {input_local_filename} -> {output_local_filename} with parameters: {parameters}")
    pm.execute_notebook(
        input_path=input_local_filename,
        output_path=output_local_filename,
        log_output=True,
        progress_bar=False,
        parameters=parameters,
    )

    output_bucket = "output-notebooks"  # make this a config
    print(f"Uploading {output_local_filename} to bucket {output_bucket} as {output_object_name}")
    put_file(local_path=output_local_filename, bucket=output_bucket, file_name=output_object_name)

    print("Notebook executed")


def main() -> None:

    parser = argparse.ArgumentParser(description="Run a Jupyter notebook with papermill.")

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
        help=("JSON string of parameters to pass to the notebook, " "use doublequotes on value and key"),
    )
    parser.add_argument(
        "--kernel",
        type=str,
        required=False,
        default="FREEDS",
        help=("Kernel for running the notebook. " "If not provided, 'FREEDS' kernel is used."),
    )

    args = parser.parse_args()
    if "/" in args.notebook_name:
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
        kernel=args.kernel,
    )


if __name__ == "__main__":
    main()
