# DuckDB
gotcha: if you use dbeaver to access duckDB it will take an exclusive read/write lock, you'll need to disconnect manually or set the duckdb.read_only=true in the driver properties. As described in this [stack overflow entry](https://stackoverflow.com/questions/74411716/set-read-only-connection-to-duckdb-in-dbeaver)

## Databases

We put database files in /tmp/data
We're using the "warehouse" database for most labs and the filename is expected to be in the env-variable DATASTACK_DUCKDB.
