# FREEDS-Config Service

A simple API server for managing YAML-based configuration files.

There's CRUD functionality but that's currently just for fun and exercise, it's nice to have a flask api server up and running in case we want to do something else. Right now we're only using this service to retrieve configs. I do all the editing directly in the files.

so it could as well be an nginx serving up files from the mounted directories.

It could however not be folder in a well known location, airflow DockerOperator is unable to mount host directories (on mac).
Using env values is an alternative but that's cumbersome, any new config for whatever we want to do in airflow would need to be passed into the airflow container and then the DockerOperator would pass it to the executing docker container. This way we just add the config value in a file and the code in the executing container can start using it without modifing the airflow code.


## Overview

FREEDS-Config provides a RESTful API for creating, reading, updating, and deleting configuration files stored in YAML format. It's built using Flask and OpenAPI/Swagger for documentation.

## Features

- CRUD operations for configuration files
- Automatic API documentation via Swagger UI and ReDoc
- Docker containerization for easy deployment
- YAML-based storage with file locking for concurrent access
- Management of files with secrets in separate folder, allowing non secret configs to be pushed to git.


The API will be available at:
- http://localhost:8005/api/configs/
- http://localhost:8005/swagger-ui (API documentation)
- http://localhost:8005/redoc (Alternative API documentation)

### API Endpoints

- `GET /api/configs/` - List all configuration files
- `GET /api/configs/{config_name}` - Get a specific configuration

### secrets
If a file has an api key or something in it, put it in the local_configs folder and it stays on your disk.
freeds-config looks in:
freeds-config/configs/ (which is a git repo)
freeds-config/local_configs/ (which only lives on your machine)

### troubleshooting

    source <(freeds env) && docker compose exec api bash
