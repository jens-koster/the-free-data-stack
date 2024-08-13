# Meltano

pipx is recommended

    pipx install "meltano"


## Extractors

### github
    meltano add extractor tap-github

## Targets

### DuckDB
https://hub.meltano.com/loaders/target-duckdb--jwills/

    meltano add loader target-duckdb
    meltano config target-duckdb set path "${DATASTACK_DUCKDB}"
