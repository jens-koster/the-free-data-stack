# The Free Datastack (fds)
My various tinkering with open source data tools. I'm aiming at a open source pluggable lab stack, it's still a bit rough a round the edges, but I had it working!

* Supported on mac, possibly Linux, will not work on Windows.

I am maintaining a list in notion of free stack tools, might be of interest:
https://ambitious-bowl-f63.notion.site/Free-Datastack-Catalogue-1bc65454dd3f80f4a8e7cfda2edcb4a9?pvs=4


# Rationale
A data stack is a collection of services, like spark, postgresql, airflow, redis, S3 storage, dbt and so on. When you want try out for example airflow you'll find a docker compose file firing up the entire stack needed to run airflow, with no connectivity to other local services. Many stacks depend on basic services like postgres and redis, I want to break the stacks up and re-use the same postgres for all services depending on it. I want all services on the same docker network with unique and consistent hostnames.
Most services come with a web ui on a typical web port, that I want to map to localhost. Let's make those ports unique in the entire fds. Actually, we generalize that to say all services should be able to run in parallel without conflicts.
In development it really helps if services are callable using the same hostname on the host as in the docker network. It doesn't solve every situation, but it really makes it easier. That's easily accomplished by mapping them in the hosts file.
After dealing with spark it becomes clear we need the ability to define storage on the exact same location on the host and the containers, realtive paths and "user" paths have proven unreliable. We require a known root folder where freeds can create any folder needed. The containers will create the exact same folder structure, most folders will are mounted from parallel structure on the host.
The "production" way of doing this is to use an object storage. So, we'll provide an S3 service which will be used for for data, notebooks and other things it works well for.

# Architecture
Each service has a docker compose file starting up only that service.
A docker network is created outside the docker compose files and all containers simply refer it.
A list of all ports used by different services is maintained here, as services are added ports are configured and re-mapped to make every hostname and port used globally unique.
Each stack is given a name defined in configuration file, specifying the folder names of services in the stack. A python CLI is created to run docker compose in each folder, it changes the current directory before calling docker compose so relative paths can be used.

# Pipeline notebooks
The notebooks making up the pipelines (extract, bronze, silver, gold, etc) go in a separate repo; https://github.com/jens-koster/pipe-dreams.
This keeps freeds clean and is also the lab for doing things by the book, there's a ton of commit hooks linting and sorting things. That gets a bit tedious for the freeds repo, I know, I should have that here as well ...mea culpa.

There's the papermill service to execute these parameterized notebooks form s3 and deliver the result on s3.
Might require some love and attention but it all worked nicely from airflow DockerOperator at one point...

# Labs
## Wikipedia Pageviews
Currently considered "done".
Documentation: https://github.com/jens-koster/the-free-data-stack/blob/main/docs/labs/wikipedia_pageviews.md

## Øresund Train Spotter
In exploration phase.

Repo: https://github.com/jens-koster/freeds-train-spotter

Project: https://github.com/users/jens-koster/projects/3


# Setup - getting started

    git clone https://github.com/jens-koster/the-free-data-stack.git
    cd the-free-data-stack
    # setup folders, docker network and python venv
    source setup.sh

    # ... TBD

    # fire it up!
    python3 ./freeds-cli/freeds.py up

    # to shut everything down:
    python3 ./freeds-cli/freeds.py down


# create the root freeds folder
    After various attempts I came to the conclusion that we need a folder that can be on the same path in all of freeds, dockers, host, everything.
    Not including any current-user stuff, not a tmp folder that is magically recreated on restart. a simple persistent file folder for storing things...
    Especially spark is very finicky about...well everything, which includes folder locations.

    So, at least on mac you need to be root to create top level folders and then make yourself owner of that folder.

    sudo mkdir /opt/freeds
    sudo chown -R $USER:$USER /opt/freeds

    Docker desktop on mac protects the host by only allowing mounting on a few default folders like /tmp and ~, so you need to add /opt/freeds to the list in Settings->Resources->File sharing.

# plugin folder structure
Plugins reside in a repo, which has a git url.
Assumptions (to keep things simple):
* all repos are cloned to the same root dir, they need not be alone in it, but all are in the same directory.
* the git repo is cloned to a directory named as the repo, repo names are not required to be the same as the github repo names except for the core freeds repos. Allowing name clashes to be resolved in repos.yaml.
* plugins are in directories directly under a repo dir, one plugin in each directory. There can be other folders in the repo. (but plugin names are unique under the repo name)
* plugin directories are named after the plugin, plugin names are defined in config files. One config file per repo.
* There's a plugins.yaml config file that define the plugins in the-free-data-stack.
* *There's a repos.yaml defining the other plugin repos*
* there's a docker-compose.yaml file in every plugin directory
* there's a README.md in every plugin directory

How to find the roots:
*nyi: a ~/.freeds file is created poiting to a location for /opt/freeds and the full path to the folder with the repos.*
Default freeds searches the current directory and upwards to find the parent of 'the-free-data-stack' dir for repo root. It assumes '/opt/freeds' for the root of the app files.

# Networking

All docker compose files use a common network named `freeds-network`.
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
- 8005 - freeds-config on:
  - http://127.0.0.1:8005/swagger-ui
  - http://127.0.0.1:8005/redoc
  - http://127.0.0.1:8005/api/configs
- 8006 - minio S3 on http://127.0.0.1:8006
- 8007 - redis insight on http://127.0.0.1:8007
- 8008 - devpi python package index

- 8010 - spark master on http://127.0.0.1:8010
- 8011 - spark worker 1 on http://127.0.0.1:8011
- 8012 - spark worker 2 on http://127.0.0.1:8012
- 5432 - postgreSQL, reserved schemas:
  - airflow
- 5555 - Celery flower(airflow thing, not tested)
- 6379 - redis
- 7077 - spark master
- 9900 - minio S3 - default minio port is 9000 but that is used by vs code, so it's set to 9000.

## host mappings
Find out how to edit the hosts file on your os;

    # mac:
    sudo nano /etc/hosts



and add the following mappings:

    127.0.0.1 spark-worker-1
    127.0.0.1 spark-worker-2
    127.0.0.1 spark-master
    127.0.0.1 s3-minio
    127.0.0.1 freeds-config
    127.0.0.1 postgresql
    127.0.0.1 devpi
    127.0.0.1 redis
    127.0.0.1 redisinsight

# Storage
Anything that can reasonably go on S3 shoud do so, we use minio S3 to provide a local (and free) S3 storage.
Sharing data on disk between dockers turned out not to solve all use cases. The airflow DockerOperator where you do "Docker in Docker", I could not get the spawned docker to mount a host directory. S3 and the config api server means we only need to supply the config server url to any docker in docker or host container. It is also easier editing a config on file and then directly using it in the code, rather than piping things thorugh env variables and whatnot. FREEDS is "opinionated", flexibility is traded for simplicity where it makes sense.

The default storage location root is ~/freeds, there is not yet an env variable to control the root. That will come...

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
