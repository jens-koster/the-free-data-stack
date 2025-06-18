## papermill plugin
papermill is a tool for running parameterized notebooks: https://papermill.readthedocs.io/en/latest/

papermill takes a notebook, parameters and an output filename.
It runs the notebook and stores the resulting notebook at the specified location, i.e. the original notebook is not modified.

freeds papermill plugin is intended for use with airflow DockerOperator and as a jupyter server for running your spark notebooks.

Notebooks and output notebooks are now on S3 as is the data itself. use freeds nb deploy to copy the pipe-dreams repo to s3. (or any repo you configure)

The notebooks are maintained in the pipe-dreams repo: https://github.com/jens-koster/pipe-dreams

# Jupyter server for development in vs code
Spark is exteemely finicky on versions of java, pyspark and everything.
For this reason, the papermill plugin is actually based on the image from the spark plugin. Ensuring *everything* is the same. This also means you don't have to meddle with your local java version which might be a dealbreaker. Also no need to worry that much about the exact pyspark or python version you're on.
If you need new non-spark dependencies, I'd consider creating a separate jupyter server without spark. If you start installing stuff in the spark based papermill container, you will inevitably break spark with a bunch of unintelligable unrelated error messages and spend hours troubleshooting it, to find it's your new dependency installing an obscure version of something that breaks spark. Spark always breaks.

Anyway. In vs code you can select kernel, you pick "Existing jupyter server" and enter http://127.0.0.1:8888. On my mac this shows as "Python 3 (ipykernel)" but you can see the 127.0.0.1 in the tooltip to know you're actually running in the server.

# Papermill container for running notebooks

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
