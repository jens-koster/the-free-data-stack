
#Airflow
## todo:
* stop using folders in /tmp/airflow, no need since we always run docker compose in the airflow folder.
* KISS: also, just let the logs be created in the airflow folder until there's a reason not to...


    #Start and stop airflow including the postgres dependency
    docker compose --file ./PostgreSQL/docker-compose.yaml up -d &&  docker compose --file ./Airflow/docker-compose.yaml up -d

    docker compose --file ./Airflow/docker-compose.yaml down &&  docker compose --file ./PostgreSQL/docker-compose.yaml down
