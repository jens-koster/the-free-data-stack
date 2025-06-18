# Spark


## General learnings
Spark is extremely finicky and expects EVERYTHING to have the exact same version, same url and same path in all places. i.e. not only in the spark nodes in the docker network but also on the driver.
There's a jupyter server based on the same docker image as the spark cluster provided as a freeds plugin to help with this.
Include the jupyter plugin in your stack and point your pyspark notebook kernel at the jupyter-spark server and your code will execute using the exact same spark, pyspark, java and scala versions as the cluster uses.

For along time I attempted to run a local pyspark notebook against the cluster, I tell you, that way madness lies...! At least if you're a beginner at running spark like I am. Spark you can get aligned, but when you add s3, hive catalog and delta tables, things wuickly escalatte with mismatched jars. Mismatched log4j jars will cause spark to fail silently.

I'd say you either run pyspark 100% locally using local[*] as your master, or execute it on the jupyter server t use the spark cluster. It's quite easy to switch between the two, the get_saprk_connection provided in freeds has a "use_local" flag for switching to "local[*]". Eliminating the cluster comes in handy for troubleshooting, and might even be my preference for the development phase. Make sure things run on local[*] before attempting the to run on the cluster.
Any packages you add for your notebook will of course need to be added in the jupyter server as well.

## Networking and getting the spark ui working

### Align the host names
In general we want the same host names available on the host as in the docker network.

Find out how to edit the hostfile on your os and add these (there's more to add, but these are the ones used by spark):

    127.0.0.1 spark-worker-1
    127.0.0.1 spark-worker-2
    127.0.0.1 spark-master
    127.0.0.1 s3-minio
    127.0.0.1 tfds-config

This makes anything running on your host, like the notebooks, resolve the host names to the same service as your spark containers living in the docker network.
It's also part of making the spark web ui work from within the container.

### Align the port numbers
Secondly the port numbers must match up, it's not possible to re-map portnumbers inside the docker network. So all services must be configured to use a portnumber that is also free on your host.

### Spark ports and the spark webui
To get the spark web ui working there's a few things to tweak.
Spark nodes by default uses ip addresses to refer each other, also in the web ui. these ip:s are internal to the docker network and have no meaning on the host.
Setting this env variable set to the service name. This makes spark nodes use host names to refer each other, also in the web ui.

    - SPARK_LOCAL_HOSTNAME=spark-worker-1

Spark workers default to 8081 for the web ui and spark master to 8080. Even if we could let spark master have 8080 we can't have the two workers on the same port on the host.
All webui:s in freeds are put in the 8001+port range, we put spark on spark master on 8010 and workers on 8011 and 8012.
The env value `SPARK_MASTER_WEBUI_PORT` us used for master and  `SPARK_WORKER_WEBUI_PORT` for the workers.

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

  For the webui to work on your you need the mapping of host names to 127.0.0.1 in your hosts file as described above in "Align the host names".


# setup spark to use delta
https://docs.delta.io/3.0.0/quick-start.html#set-up-apache-spark-with-delta-lake

https://repo1.maven.org/maven2/io/delta/delta-core_2.12/2.1.0/delta-core_2.12-2.1.0.jar
download delta-core_2.12-2.1.0.jar

# get the jars built into the image
We're using coursier to get the jars. Check the jar.sh script to see what we're currently using.
There's a lot of logic to clean up and get a working set of jars all over the place.
This includes copying the jars from the docker image and merging that set with the ones we download for delta, hive and s3.
It's was hard getting that right, where the main learning was that our favourite genAI friends do some serioue mansplaining and hallucinating when it comes to spark. I'm taking that to be a mirror of the real world, there's a lot of confusion on spark configs and what verisons work together. My tactic was to provide details in the prompt, submit the coursier download script and the spark conf file.

It is not sufficient to install the jars using pip for pyspark packages, you get the jars but spark seem not to find them. It worked fine locally when using pyspark, but the spark cluster did not find them.

#### delta table
io.delta:delta-spark_2.12
Provides delta table functionality, that's the preferred way to store the data.

#### S3
* org.apache.hadoop:hadoop-aws

* org.apache.hadoop:hadoop-common

* com.amazonaws:aws-java-sdk-bundle

These three provide the S3 functionality. We use s3 to store extracted source files and as our warehouse for the created delta tables.
