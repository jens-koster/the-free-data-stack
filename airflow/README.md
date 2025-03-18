#Airflow

    #Start and stop airflow including the postgres dependency
    docker compose --file ./PostgreSQL/docker-compose.yaml up -d &&  docker compose --file ./Airflow/docker-compose.yaml up -d

    docker compose --file ./Airflow/docker-compose.yaml down &&  docker compose --file ./PostgreSQL/docker-compose.yaml down
