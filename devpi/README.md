# devpi - local python package index

    docker-compose build
    docker-compose run --rm --entrypoint /bin/bash devpi
    #inside the container (serverdir must be set to mounted directory or everything is lost on recreate of the container):
    devpi-init --serverdir /data
    exit
    # then we're ready to start the server
    docker-compose up -d


## setting up tfds index and poetry user
    insude the cli container, while the server container is running.

    devpi use http://devpi:8008
    devpi login root --password=''
    devpi index -c tfds bases=root/pypi
This creates a writable index: root/tfds that inherits (proxies) from PyPI.

now move on to create a poetry user:
    devpi user -c poetry password=yourpassword
    # and grant access to the root/tfsd index
    devpi index root/tfds acl_upload=poetry acl_toxresult_upload=poetry

    # configure devpi and credentials for poetry, these config are global for all poetry projects.
    poetry config repositories.devpi http://127.0.0.1:8008/root/tfds/
    poetry config http-basic.tfds poetry yourpassword


## poetry build
Since the config is global you just need to tell poetry to use devpi when publishing.

    poetry build
    poetry publish -r devpi
