# ClickHouse
[Installation instuctions](https://clickhouse.com/docs/en/install)

[docker hub](https://hub.docker.com/r/clickhouse/clickhouse-server/)


    docker run --rm
        -e CLICKHOUSE_DB=
        -e CLICKHOUSE_USER=stacker
        -e CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1
        -e CLICKHOUSE_PASSWORD=jazzworkd
        -p 127.0.0.1:9000:9000/tcp
        -p 127.0.0.1:9000:9000/tcp
        clickhouse/clickhouse-server
