# The Free Datastack (fds)
For a given value of "free" of course. fds is all about trying out tools available at no cost, I have no ideological issues with using free versions of commercial tools. As the Swedish (food related) saying goes: "_free is delicious_"



### Prerequisite software
### pipx

it is recommended to use your os packagemanager (see the [realpython installation guide](https://realpython.com/python-pipx/#install-pipx-as-a-standalone-tool)
)

This will also do the trick:


    python -m pip install pipx

### required environment variables
    export DATASTACK_ROOT="/location/of/the/folder/datastack"
    export DATASTACK_DUCKDB="${DATASTACK_ROOT}/DuckDB/data/warehouse.duckdb"
