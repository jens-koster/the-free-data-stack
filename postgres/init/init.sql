--  docker exec -it postgres psql -U airflow -d postgres -f /docker-entrypoint-initdb.d/init.sql
create database airflow;
create database iceberg;
create database jaffle_shop;
SELECT datname as database_name FROM pg_database WHERE datistemplate = false;




/*
CREATE USER kafka WITH PASSWORD 'jazzword';

CREATE DATABASE kafka_db OWNER kafka;

GRANT ALL PRIVILEGES ON DATABASE kafka_db TO kafka;
GRANT USAGE ON SCHEMA public TO kafka;
GRANT CREATE ON SCHEMA public TO kafka;
*/
