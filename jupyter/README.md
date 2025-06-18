# jupyter plugin
Notebook runner server and jupyter server.

## Jupyter server for development in vs code
Spark is exteemely finicky on versions of java, pyspark and everything.
For this reason, the jupyter plugin provides a container based on the same image as the spark cluster, `jupyter-spark`. Ensuring *everything* is the same.

If you need new non-spark dependencies, I'd consider creating a separate jupyter server without spark. If you start installing stuff in the jupyter-spark container, you will sooner or later break spark in some obscure way. Getting a bunch of unintelligable unrelated error messages and spend hours troubleshooting it, to find it's your new dependency installing an old/new version of something that breaks spark. Spark always breaks.

Anyway. In vs code notebooks you can select kernel, pick "Existing jupyter server" and enter http://127.0.0.1:8888. On my mac this shows as "Python 3 (ipykernel)" but you can see the 127.0.0.1 in the tooltip to know you're actually running in the server.

## Notebook runner
Papermill is a python package for running parameterized notebooks: https://papermill.readthedocs.io/en/latest/

Papermill takes a notebook filename, parameters and an output filename. It injects the parameters, runs the notebook cells in order and stores the resulting notebook as output filername, i.e. the original notebook is not modified.

It very much resembles how databricks runs notebooks.

The notebook runner is intended for use with airflow DockerOperator. It's impossible to mount host folders when spinning up a docker from an airflow also inside docker. The notebook runner expects the input notebooks to be on s3 and will store the output notebooks in s3 as well.

The freeds CLI has functioanlity to deploy your notebooks on s3.

Notebooks are currently maintained in the pipe-dreams repo: https://github.com/jens-koster/pipe-dreams, this will change.

### book_runner.py

Run a notebook in papermill.
Intended as entrypoint to a docker container

test interactively as:

    python3 book_runner.py --notebook helloworld --parameters '{"p1":"hello", "p2":"world"}'

To test the container version, first build it:
    # in the papermill folder
    freeds dc -s . build
    # or from freeds folder
    freeds dc -s papermill build

then run the helloworld notebook in a container

    docker compose run book-runner --notebook 'helloworld' --parameters '{"p1":"hello", "p2":"world"}'

to open a shell inside a docker for troubleshooting dependencies.

    docker run --rm -it --entrypoint /bin/bash freeds/jupyter-spark:latest

To configure a venv as jupyter kernel (this is done in the Dockerfile):
    pip install ipykernel
    python -m ipykernel install --user --name=.venv --display-name "freeds 3.12.x"

The --display-name is what will appear in the Jupyter Notebook interface.
