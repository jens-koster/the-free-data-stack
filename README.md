# The Free Datastack (fds)
My various tinkering with open source data tools.
Each product has a docker compose file, all use the same network so any combination should be able to coummunicate. I'm not yet sure how to deal with configuring different combinations.


# Networking
All docker compose files use a common network named `tfds-network`.
There's no "create if not exists" for networks in docker-compose so it needs to be created stand alone before firing up anything else. It is included in `setup.sh`

## port allocations
Port number mappings ae kept globally unique, allowing us to run any docker-compose files in parallel withtout port clashes.
This is the global list of who gets what port:
    8001 - airflow web ui
    8002 - postgres web ui
    8003 - jupyter web ui

    5432 - postgres, let's assume we'll only ever have to fire up one postgres instance and all can share that
    7077 - spark master

# Storage
## directory mapping
Directories used by more than one tool or stack should be symlinked and referred in /tmp. Relative always mess things up.
You'll need to create some directories and symlink others. This way all paths can be hardcoded which makes a lot of things easier.

folder to create:


    # DuckDB data
    mkdir -p /tmp/DuckDB

    # DuckDB data
    mkdir -p /tmp/postgres

folders to symlink:

    # data sets folder, some
    ln -s "$(pwd)/_data" /tmp/data



# Data sets
Small datasets should be comitted in git, bigger ones documented here:

All data shoule be referred under /tmp/data, for portability.

### Prerequisite software
### pipx

it is recommended to use your os packagemanager (see the [realpython installation guide](https://realpython.com/python-pipx/#install-pipx-as-a-standalone-tool)
)

This will also do the trick:


    python -m pip install pipx

### required environment variables
    export DATASTACK_ROOT="/location/of/the/folder/datastack"
    export DATASTACK_DUCKDB="${DATASTACK_ROOT}/DuckDB/data/warehouse.duckdb"
