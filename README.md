# The Free Datastack (fds)
My various tinkering with open source data tools.
I'm trying to work and keep each product folder separately runnable. You'll initially find a lot of code copied from the local docker compose to the "stack" ones.

# port allocations
8001 - airflow web ui
5432 - postgres, let's assume we'll only ever have to fire up one postgres instance and all can share that

# directory mapping
Directories used by more than one tool or stack should be symlinked and referred in /tmp. Relative always mess things up.

# Data sets
Small datasets should be comitted in git, bigger ones documented here:

All data shoule be referred under /tmp/data, for portability.

    ln -s "$(pwd)/_data" /tmp/data


### Prerequisite software
### pipx

it is recommended to use your os packagemanager (see the [realpython installation guide](https://realpython.com/python-pipx/#install-pipx-as-a-standalone-tool)
)

This will also do the trick:


    python -m pip install pipx

### required environment variables
    export DATASTACK_ROOT="/location/of/the/folder/datastack"
    export DATASTACK_DUCKDB="${DATASTACK_ROOT}/DuckDB/data/warehouse.duckdb"
