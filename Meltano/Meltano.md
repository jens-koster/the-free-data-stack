# Meltano

# Usage

    # meltano must be run in the meltano project folder
    cd "${DATASTACK_ROOT}/Meltano/meltano-stack"

    # github->DuckDB
    cd "meltano-stack
    meltano run tap-github target-duckdb




# Setup
Use the [step by step guide by Meltano](https://docs.meltano.com/getting-started/)

If this is not your first rodeo, the commands needed are all in this guide

    pipx install "meltano"


### Extractors

#### github
    meltano add extractor tap-github
    meltano config tap-github set --interactive

### Targets

#### DuckDB
https://hub.meltano.com/loaders/target-duckdb--jwills/

    meltano add loader target-duckdb
    meltano config target-duckdb set path "${DATASTACK_DUCKDB}"



