# Postgresql

A common postgres server for all of freeds.

reserved schemas:

* airflow - for, well, airflow.
* spark_metastore - hive metastore backend database for the spark service.



    `CREATE USER freeds WITH PASSWORD 'pwd';`

    `GRANT ALL PRIVILEGES ON DATABASE airflow TO freeds;`

    `GRANT ALL PRIVILEGES ON DATABASE spark_metastore TO freeds;`
