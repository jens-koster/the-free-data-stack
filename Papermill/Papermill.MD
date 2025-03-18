# Papermill container for running notebooks

Run a notebook in papermill.
Intended as entrypoint to a docker container

test interactively as:

    python3 book_runner.py --notebook helloworld --parameters '{"p1":"hello", "p2":"world"}'

To test the container version, first build it:

    docker compose build

then run the helloworld notebook in a container

    docker compose run book-runner --notebook 'helloworld' --parameters '{"p1":"hello", "p2":"world"}'

to open a shell inside a docker for troubleshooting dependencies.

    docker compose run --remove-orphans --rm -it --entrypoint /bin/bash book-runner
