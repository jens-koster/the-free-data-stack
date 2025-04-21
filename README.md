# The Free Datastack (fds)
My various tinkering with open source data tools.
Each product has a docker compose file, all use the same network so any combination should be able to coummunicate. I'm not yet sure how to deal with configuring different combinations.

# Setup - getting started

    git clone https://github.com/jens-koster/the-free-data-stack.git
    cd the-free-data-stack
    # setup folders, docker network and python venv
    source setup.sh
    # make sure you have a fresh build of the docker images
    python3 ./tfds-cli/tfds.py build
    # fire it up!
    python3 ./tfds-cli/tfds.py up

    # to shut everything down:
    python3 ./tfds-cli/tfds.py down


# create the root tfds folder
    After various attempts I came to the conclusion that we need a folder that can be on the same path in all of tfds, dockers, host, everything.
    Not including any current user stuff, not a tmp folder that is magically recreated on restart. a simple persistent file folder for storing things...
    Especially spark is very finicky about...well everything, which includes folder locations.

    So, at least on mac you need to be root to create top level folders and then make yourself owner of that folder.

    sudo mkdir /opt/tfds
    sudo chown -R $USER:$USER /opt/tfds

    Docker desktop on mac protects the host by only allowing mounting on a few default folders like /tmp and ~, so you need to add /opt/tfds to the list in Settings->Resources->File sharing.


# Networking
All docker compose files use a common network named `tfds-network`.
There's no "create if not exists" for networks in docker-compose so it needs to be created stand alone before firing up anything else. It is included in `setup.sh`

## port allocations
Port number mappings are kept globally unique, allowing us to run any ports of the stack together without port clashes.
All ports in odcker shoud be explicitly mapped to 127.0.0.1 on the host, to avoid exposing anything outside the local host.

Web ui:s are put on 8000+ ports, even if their standard port is free. There's a point in moving everything away from 80 and 8080.

Services keep their standard port as far as possible.

This is the global list of who gets what port:

- 8001 - airflow web ui on http://127.0.0.1:8001
- 8002 - postgres web ui on http://127.0.0.1:8002
- 8003 - jupyter web ui on http://127.0.0.1:8003
- 8004 - s3 ninja on http://127.0.0.1:8004/ui
- 8005 - tfds-config on:
  - http://127.0.0.1:8005/swagger-ui
  - http://127.0.0.1:8005/redoc
  - http://127.0.0.1:8005/api/configs
- 8006 minio S3 on http://127.0.0.1:8006
- 8010 - spark master on http://127.0.0.1:8010
- 8011 - spark worker 1 on http://127.0.0.1:8011
- 8012 - spark worker 2 on http://127.0.0.1:8012
- 5432 - postgreSQL, reserved schemas:
  - airflow
- 5555 - Celery flower(airflow thing, not tested)
- 7077 - spark master
- 9000 - minio S3

# Storage
Anything that can reasonably go on S3 shoud do so, we user minio
Sharing data on disk between dockers turned out not to solce all use cases. The airflow DockerOperator where you do "Docker in Docker", I could not get the spawned docker to mount a host directory. S3 and the config api server means we only need to supply the config server url to any docker in docker or host container. It is also easier editing a config on file and then directly using it in the code, rather than piping things thorugh env variables and whatnot. TFDS is "opinionated", flexibility is traded for simplicity where it makes sense.

The default storage location root is ~/tfds, there is not yet an env variable to control the root. That will come...

S3 is first choice for any data shared between stack service.

We'll see what to do with DuckDB, you can create a readonly connection to it on s3. We could setup a duckdb container that performs the loading of the database and then publish it to s3 for readonly access...

postgreSQL uses a docker managed volume for storage.

### Prerequisite software
### pipx

it is recommended to use your os packagemanager (see the [realpython installation guide](https://realpython.com/python-pipx/#install-pipx-as-a-standalone-tool)
)

This will also do the trick:

    python -m pip install pipx

### pyenv
You'll probably need to adjust your python version to match whatever you have in spark, it's insanely picky about those things.

### java
You definitely need to adjust your java version to spark. see more in the spark readme.
