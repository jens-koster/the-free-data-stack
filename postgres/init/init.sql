--  docker exec -it postgres psql -U airflow -d postgres -f /docker-entrypoint-initdb.d/init.sql
create database airflow;
create database spark_metastore;
SELECT datname as database_name FROM pg_database WHERE datistemplate = false;