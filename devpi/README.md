# devpi - local python package index

    docker-compose build
    docker-compose run --rm --entrypoint /bin/bash devpi
    #inside the container (serverdir must be set to mounted directory or everything is lost on recreate of the container):
    devpi-init --serverdir /data
    exit
    # then we're ready to start the server
    docker-compose up -d


## setting up freeds index and poetry user
    insude the cli container, while the server container is running.

    devpi use http://devpi:8008
    devpi login root --password=''
    devpi index -c freeds bases=root/pypi
This creates a writable index: root/freeds that inherits (proxies) from PyPI.

now move on to create a poetry user:
    devpi user -c poetry password=yourpassword
    # and grant access to the root/tfsd index
    devpi index root/freeds acl_upload=poetry acl_toxresult_upload=poetry

    # configure devpi and credentials for poetry, these config are global for all poetry projects.
    poetry config repositories.devpi http://127.0.0.1:8008/root/freeds/
    poetry config http-basic.freeds poetry yourpassword


## poetry build
Since the config is global you just need to tell poetry to use devpi when publishing.

    poetry build
    poetry publish -r devpi

## debugging the conatiner

    docker exec  -it --entrypoint /bin/bash devpi



### What works:
set env variable in your host environment, affects pip but not poetry:

    export PIP_INDEX_URL=http://127.0.0.1:8008/root/freeds/
    devpi use http://devpi:8008
    devpi login root --password=''

in the dockerfiles you'll need to use this construct

    RUN pip install --trusted-host host.docker.internal --index-url http://host.docker.internal:8008/root/freeds/ --no-cache-dir -r requirements.txt

as long as the requirements.txt is not used in docker builds you can set the devpi url in requirements.txt

    --index-url http://devpi:8008/root/freeds/

for poetry you add in pyproject.toml:

    [[tool.poetry.source]]
    name = "devpi"
    url = "http://devpi:8008/root/freeds/+simple/"
    priority = "supplemental"


**host.docker.internal**: a special hostname, works on mac and apparently windows. docker build can't directly access neither the host nor the docker network. It's tricky reaching our local devpi server. The special host name allows access from docker build to the host.

**--trusted-host host.docker.internal** : bypasses pips check that the host uses https with a proper certificate

**--index-url http://host.docker.internal:8008/root/freeds/** : tells pip to use this package index

### next attempt:
This is messy... I might change to downloading the artifacts to the docker context folder before starting the build.
or building them in github actions and referring a github path from the build
or simply push it to pypi, or github index.
