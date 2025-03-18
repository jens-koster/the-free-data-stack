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
import os
import json
import papermill as pm


def execute_notebook(args):
    input = '/tmp/notebooks'
    output = '/tmp/output_notebooks'
    # Parse the parameters
    notebook = args.notebook
    print(f"Running notebook {notebook}")


    try:
        print(f"Parameters: {args.parameters}")
        parameters = json.loads(args.parameters)

    except json.JSONDecodeError:
        raise ValueError("Invalid JSON string for parameters")

    # Path to the input notebook
    input_notebook = os.path.abspath(f"{input}/{notebook}.ipynb")
    if not os.path.isfile(input_notebook):
        raise FileNotFoundError(f"Notebook {input_notebook} not found")

    # Create the output directory if it doesn't exist
    output_dir = os.path.abspath(f"{output}/{notebook}")
    os.makedirs(output_dir, exist_ok=True)
    os.path.basename(output_dir)
    output_notebook = (
        f"{output_dir}/{os.path.basename(output_dir)}_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.ipynb"
    )

    # Run the notebook with the specified parameters
    pm.execute_notebook(
        input_path=input_notebook, output_path=output_notebook, parameters=parameters
    )

    print(f"Notebook executed and saved to {output_notebook}")


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
    execute_notebook(args)


if __name__ == "__main__":
    main()
