# Spark

    docker cp spark-master:/opt/bitnami/spark/jars ./jars
    docker exec -it spark-master /bin/bash


# versions
inside the spark-master docker you run

    docker exec -it /bin/bash

    # to get spark, java and scala versions (exit using ctrl-d)
    spark-shell

    # python version
    python --version

    #pyspark verions
    pip freeze

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
    127.0.0.1 s3-minio
    127.0.0.1 tfds-config

This makes anything running on your host, like the notebooks, resolve the host names to the same service as your spark containers living in the tfds-network on docker.

## align the port numbers
Secondly the port numbers must match up, it's not possible to re-map portnumbers inside the docker network. So all services must be configured to use a portnumber that is also free on your host.

edit: after changing to minio s3 it is likelt possible to use another port for s3, we probabaly should...

Where, I found that vs code automatically start up the jupyter service on port 9000, which is also the port s3-ninja will use.
This was the final clinch before I got spark running on s3.
s3-ninja is very sparsely documented and seems not to honour the S3NINJA_PORT env variable.
Vs code seems not to honour the jupyter startup command line parameters.

Solution: there's a setting on the Jupyter extension to conrol automtic start up of the jupyter service. Uncheck that and make sure to start up s3-ninja before you run a notebook. The jupyter service seems to run just fine on whatever free port it can find.

### Spark ports and the spark webui
To get the spark web ui working there's a few things to tweak.
Spark nodes by default uses ip addresses to refer each other, also in the web ui. these ip:s are internal to the docker network and have no menaing on the host.
To each container in the spark cluster you add this env variable set to the service name. This makes spark nodes use host names to refer each other, also in the web ui.

    - SPARK_LOCAL_HOSTNAME=spark-worker-1

Spark workers default to 8081 for the web ui and spark master to 8080. Even if we could let spark master have 8080 we can't have the two workers on the same port.
We can also take the opportunity to arrange the ports for the tfds setup of putting web-ui from 8000 and up. For spark master you add the `SPARK_MASTER_WEBUI_PORT` and for the workers the `SPARK_WORKER_WEBUI_PORT`

so for master and the workers we'd set:

    # master
    enviroment:
      - SPARK_MASTER_WEBUI_PORT=8010
    ports:
      - "127.0.0.1:8010:8010"

    # worker 1
    enviroment:
      - SPARK_WORKER_WEBUI_PORT=8011
    ports:
      - "127.0.0.1:8011:8011"

  For the webui to work you need the mapping of host names to 127.0.0.1 in your hosts file as described above in "Align the host names".


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

# setup spark to use delta
https://docs.delta.io/3.0.0/quick-start.html#set-up-apache-spark-with-delta-lake

https://repo1.maven.org/maven2/io/delta/delta-core_2.12/2.1.0/delta-core_2.12-2.1.0.jar
download delta-core_2.12-2.1.0.jar

# get the jars built into the image
We're using coursier to get the jars.

    brew install coursier

at the time of writing we'r egetting these:

    coursier fetch \
    io.delta:delta-spark_2.12:3.3.0 \
    org.apache.hadoop:hadoop-aws:3.3.4 \
    org.apache.hadoop:hadoop-common:3.3.4 \
    com.amazonaws:aws-java-sdk-bundle:1.12.262 \
    org.postgresql:postgresql:42.6.0 \
    org.apache.hive:hive-metastore:2.3.9 \
    org.apache.hive:hive-exec:2.3.9 \
    org.apache.hive:hive-common:2.3.9 \
    org.datanucleus:datanucleus-core:4.1.17 \
    org.datanucleus:datanucleus-api-jdo:4.2.4 \
    org.datanucleus:datanucleus-rdbms:4.1.19 \
    javax.jdo:jdo-api:3.2.0-m3 \
    commons-pool:commons-pool:1.6 \
    --classpath | tr ':' '\n' | while read jar; do cp "$jar" package_jars/; done


**io.delta:delta-spark_2.12**

provides delta table functionality, that's the preferred way to store the data.


**org.apache.hadoop:hadoop-aws**

**org.apache.hadoop:hadoop-common**

**com.amazonaws:aws-java-sdk-bundle**

These provide the S3 functionality. We use s3 to store extracted source files and as our warehouse for the created delta tables.

    org.postgresql:postgresql
    org.apache.hive:hive-metastore
    org.apache.hive:hive-exec
    org.apache.hive:hive-common
    org.datanucleus:datanucleus-core
    org.datanucleus:datanucleus-api-jdo
    org.datanucleus:datanucleus-rdbms
    javax.jdo:jdo-api
    commons-pool:commons-pool**
This bunch was added to support Hive catalog on postgres.