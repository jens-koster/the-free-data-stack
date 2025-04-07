# Spark

    docker cp spark-master:/opt/bitnami/spark/jars ./jars
    docker exec -it spark-master /bin/bash




# Troubleshooting

    docker exec -it spark-master /bin/bash
## general learnings
spark is extremely finicky and exepects EVERYTHING to have the exact same version, url, path in all places. i.e. not only in the docker network but also on the host (the driver).

## align the host names
We have to get stuff like the s3-ninja host name be exactly the same on the docker network and on localhost.
Find out how to edit the hostfile on your os and add:

    127.0.0.1 spark-worker-1
    127.0.0.1 spark-worker-2
    127.0.0.1 spark-master
    127.0.0.1 s3-ninja
    127.0.0.1 tfds-config

This makes anything running on your host, like the notebooks, resolve the host names to the same service as your spark containers living in the tfds-network on docker.

## align the port numbers
Secondly the port numbers must match up, it's not possible to re-map portnumbers inside the docker network. So all services must be configured to use a portnumber that is also free on your host.
Where, I found that vs code automatically start up the jupyter service on port 9000, which is also the port s3-ninja will use.
This was the final clinch before I got spark running on s3.
s3-ninja is very sparsely documented and seems not to honour the S3NINJA_PORT env variable.
Vs code seems not to honour the jupyter startup command line parameters.

Solution: there's a setting on the Jupyter extension to conrol automtic start up of the jupyter service. Uncheck that and make sure to start up s3-ninja before you run a notebook. The jupyter service seems to run just fine on whatever free port it can find.


## align spark versions
Make sure the one installed in your venv matches exactly the on in your dockers.
how to check the version in your docker:

    docker exec -it spark-master spark-submit --version

and same command to check it locally:

    spark-submit --version

## align java versions
Similar to how you checked the spark version you can check the java and python versions.

For java it is important the the major and minor jdk versions are the same.

    # in docker
    docker exec -it spark-master java --version
    # locally
    java --version

If major versions differ, you'll have to deal with it. In my case I simply uninstalled the java sdk I had and used brew to install the one in my spark cluster. How to support a different java version in your dev project is out of scope for tfds right now.

## align the jar versions
Easiest way to ensure you're using the same jars is to simply copy the lot out of the docker container and refere those in your notebooks.
It's quite a lot I recommend adding `jars/` to your .gitignore and not committing them to git.

    cd spark
    docker cp spark-master:/opt/bitnami/spark/jars ./jars


## Align python versions
    # in docker
    docker exec -it spark-master python3 --version
    # locally
    python3 --version

if python versions differ I'd recommend using pyenv to get the exact same version as your spark engine.
At the time of writing my spark was on 3.11.8

    # get the python version installed
    pyenv install 3.11.8

    # get it your current "python3"
    pyenv global 3.11.8

    # create your venv
    python3 -m venv .venv

    # activate it
    source ./.venv/bin/activate

    # upgrade pip
    pip install --upgrade pip
    # before installing python dependencies, check out requirements.txt
    # and ensure the pyspark versaion matches your spark version like so:
    # pyspark==3.5.0

    # install requirements
    pip install -r requirements.txt
