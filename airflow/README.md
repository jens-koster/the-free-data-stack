
#Airflow

The docker compose is based on the official docker compose file and is a bit bloated for tfds.
https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html#fetching-docker-compose-yaml

It is intended that we use only builtin operators and the DockerOperator to keep the airflow dependencies small.
DockerOperator runs docker in docker, i.e. it uses the hsot docker service, which comes with some challenges since at least on mac you can't mount any folders on the host in the docker-in-docker container.
We're circumventing this by running our own config api server and an s3 server, i.e. storage is primarly network based. No docker you want to run from airflow can have mounts. Never tried out whether docker allows them to have volumes for persistent storage...


cleaning out the db

    docker exec -it airflow-webserver airflow db reset -y
