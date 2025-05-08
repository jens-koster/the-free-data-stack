# The Free Datastack (fds)
My various tinkering with open source data tools. I'm aiming at a open source pluggabel lab stack, right now it's half way.
* Documentation is a bit all over the place, it will be consolidated.
* Packaging could be smoother
* Supported on mac, possibly Linux, will not work on Windows.

# Rationale
A data stack is a collection of services, like spark, postgresql, airflow, redis, S3 storage, dbt and so on. When you want try out for example aitflow you'll find a docker compose file firing up the entire stack needed to run airflow, with no connectivity to other local services. Many stacks depend on basic services like postgres and redis, I want to break the stacks up and re-use the same postgres for all services depending on it. I want all services on the same docker network with unique and consistent hostnames.
Most services come with a web ui on a typical web port, that I want to map to localhost. Let's make those ports unique in the entire fds. Actually, we generalize that to say all services should be able to run in parallel without conflicts.
In development it really helps if services are callable using the same hostname on the host as in the docker network. It doesn't solve every situation, but it really makes it easier. That's easily accomplished by mapping them in the hosts file.
After dealing with spark it becomes clear we need the ability to define storage on the exact same location on the host and the containers, realtive paths and "user" paths have proven unreliable. We require a known root folder where tfds can create any folder needed. The containers will create the exact same folder structure, nost folders will are mounted from parallel Structure on the host.
The "production" way of doing this is to use an object storage. So, we'll provide an S3 service which will be used for for data, notebooks and other things it works well for.

# Architecture
Each service has a docker compose file starting up only that service.
A docker network is created outside the docker compose files and all containers simply refer it.
A list of all ports used by different services is maintained here, as services are added ports are configured and re-mapped to make every hostname and port used globally unique.
Each stack is given a name defined in configuration file, specifying the folder names of services in the stack. A python CLI is created to run docker compose in each folder, it changes the current directory before calling docker compose so relative paths can be used.

# Pipeline notebooks
The notebooks making up the pipelines (extract, bronze, silver and gold) go in a separate repo; https://github.com/jens-koster/pipe-dreams.
This keeps tfds clean and is also the lab for doing things by the book, there's a ton of commit hooks linting and sorting things. That gets a bit tedious for the tfds repo, I know I should ...mea culpa.

There's the papermill service to execute these parameterized notebooks form s3 and deliver the result on s3.
Might require some love and attention but it all worked nicely from airflow DockerOperator at one point...

# Setup - getting started

    git clone https://github.com/jens-koster/the-free-data-stack.git
    cd the-free-data-stack
    # setup folders, docker network and python venv
    source setup.sh

    # ... TBD

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
- 8007 redis insight on http://127.0.0.1:8007

- 8010 - spark master on http://127.0.0.1:8010
- 8011 - spark worker 1 on http://127.0.0.1:8011
- 8012 - spark worker 2 on http://127.0.0.1:8012
- 5432 - postgreSQL, reserved schemas:
  - airflow
- 5555 - Celery flower(airflow thing, not tested)
- 6379 - redis
- 7077 - spark master
- 9000 - minio S3 - change this! vs code sometimes start something on multiple ports around 9000 and minio allows port to be configured.

## host mappings
Find out how to edit the hosts file on your os;

    # mac:
    sudo nano /etc/hosts



and add the following mappings:

    127.0.0.1 spark-worker-1
    127.0.0.1 spark-worker-2
    127.0.0.1 spark-master
    127.0.0.1 s3-minio
    127.0.0.1 tfds-config
    127.0.0.1 postgresql

# Storage
Anything that can reasonably go on S3 shoud do so, we use minio S3 to provide a local (and free) S3 storage.
Sharing data on disk between dockers turned out not to solve all use cases. The airflow DockerOperator where you do "Docker in Docker", I could not get the spawned docker to mount a host directory. S3 and the config api server means we only need to supply the config server url to any docker in docker or host container. It is also easier editing a config on file and then directly using it in the code, rather than piping things thorugh env variables and whatnot. TFDS is "opinionated", flexibility is traded for simplicity where it makes sense.

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
