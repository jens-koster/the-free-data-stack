# The Free Datastack (fds)
My various tinkering with open source data tools.
Each product has a docker compose file, all use the same network so any combination should be able to coummunicate. I'm not yet sure how to deal with configuring different combinations.


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
- 8010 - spark master on http://127.0.0.1:8010
- 8011 - spark worker 1 on http://127.0.0.1:8011
- 8012 - spark worker 2 on http://127.0.0.1:8012
- 5432 - postgreSQL, reserved schemas:
  - airflow
- 5555 - Celery flower(airflow thing, not tested)
- 7077 - spark master

# Storage
Anything that can reasonably go on S3 shoud do so, we user s3-ninja to emulate S3 locally. Sharing data on disk between dockers turned out to be complex and cumbersome. Especially the airflow DockerOperator where you do "Docker in Docker", the spawned docker either needs to know a common place  or get the data as a parameter. Also, S3 gives a more realistic experience for us to learn from.

## mounts and volumes
Let's try to use volumes where possible, but host mounts for stuff like postgrSQL and DuckDB, we want to manual control when that data is deleted or disappears, regardless of docker reinstalls etc.
The base folder for all shared files should be one of the few things to go in an env variable. Preferably a place in your user folder, outside that we're more likely to run into permission issues.
TBD: *Let's use real folders for the vanilla tfds setup, you can then replace them with symlinks to dev folders as needed.*


### Prerequisite software
### pipx

it is recommended to use your os packagemanager (see the [realpython installation guide](https://realpython.com/python-pipx/#install-pipx-as-a-standalone-tool)
)

This will also do the trick:

    python -m pip install pipx

### required environment variables
    export DATASTACK_ROOT="/location/of/the/folder/datastack"
    export DATASTACK_DUCKDB="${DATASTACK_ROOT}/DuckDB/data/warehouse.duckdb"
