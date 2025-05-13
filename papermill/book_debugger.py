import json
import sys
import book_runner
import os
import docker



def run_book_dev(notebook, params):
    os.environ['TFDS_CONFIG_URL'] = 'http://tfds-config:8005/api/configs'
    args = [
        'book_runner.py',
        '--notebook', notebook,
        '--parameters', json.dumps(params),
        '--kernel', '.venv'
    ]
    sys.argv = args
    book_runner.main()



def run_book_prod(notebook, params):

    client = docker.from_env()
    cmd = [
        "--notebook", notebook,
        "--parameters", json.dumps(params)
    ]

    container = client.containers.run(
        image="tfds/papermill-base:latest",
        command=cmd,
        auto_remove=True,
        network="tfds-network",
        tty=False, # for getting the logs, line by line rather tha char by char
        volumes={},
        detach=True  # for getting the logs at all
    )
    for line in container.logs(stream=True):
        print(line.decode().strip())


params_wiki_extract = {
    "execution_hour_str": '2025-03-12',
    "output_bucket": "data",
    "output_root_prefix": "wikipedia_pageviews",
    "overlap_hours": 1,
    "force_reupload": False,
}

params_hello = {
    "p1": 'book',
    "p2": "debugger"
}

nb = 'pipe-dreams/notebooks/helloworld'
nb = 'pipe-dreams/notebooks/wikipedia_pageviews/wikipedia_pageviews_extract'
p = params_wiki_extract

run_book_prod(nb, p)
# run_book_dev(nb, p)
