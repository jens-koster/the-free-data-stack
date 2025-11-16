# The Free Datastack (fds)
My various tinkering with open source data tools. I'm aiming at a open source pluggable lab stack, it's still a bit rough a round the edges.
Check out the readme in freeds CLI to get it up and working(sorry, I'll align the docs out at some point in time.): https://github.com/jens-koster/FreeDS#

* Supported on mac, possibly Linux, will likely not work on Windows.

I am maintaining a list in notion of free stack tools, might be of interest:
https://ambitious-bowl-f63.notion.site/Free-Datastack-Catalogue-1bc65454dd3f80f4a8e7cfda2edcb4a9?pvs=4

# tl:dr
To set it up, go here: https://github.com/jens-koster/FreeDS

# Rationale
A data stack is a collection of services, like spark, postgresql, airflow, redis, S3 storage, dbt and so on.

My problem has alwyas been to spend one evening getting a certain tool up and running, the I never return to actually try it out, I just fight setup issues all night. Or I get it setup and spend the rest of the night getting a decent data set into the service to..just do something.

So, now I'm going to configure each service once and for all.

There will be data to start playing eith, on S3 and kafka topics etc. My expectatio is to add one or two dockers in a already bubbling data stack and start playing with them in an hour or two.

Ideally, we'd start sharing these pluggable stack items so I can just clone a repo and start fiddling with a new tech in the stack and datasets I already know. Or the ones I chose to add my stack. Reduce cognitive load and effort to start learning a new tech.

# some tech stuff
Most services come with a web ui on a typical web port, that I want to map to localhost. Let's make those ports unique in the entire fds. Actually, we generalize that to say all services should be able to run in parallel without conflicts.
In development it really helps if services are callable using the same hostname on the host as in the docker network. It doesn't solve every situation, but it really makes it easier. That's easily accomplished by mapping them in the hosts file.
After dealing with spark it becomes clear we need the ability to define storage on the exact same location on the host and the containers, realtive paths and "user" paths have proven unreliable. We require a known root folder where freeds can create any folder needed. The containers will create the exact same folder structure, most folders will are mounted from parallel structure on the host.
The "production" way of doing this is to use an object storage. So, we'll provide an S3 service which will be used for for data, notebooks and other things it works well for.

# Architecture
Each stack item has a docker compose file starting up only that item.
A docker network is created outside the docker compose files and all containers simply refer it.
A list of all ports used by different services is maintained here, as services are added ports are configured and re-mapped to make every hostname and port used globally unique.
Each stack is given a name defined in configuration file, specifying the folder names of services in the stack. A python CLI is created to run docker compose in each folder, it changes the current directory before calling docker compose so relative paths can be used.

# Labs
Some stuff go into the central the-free-dat-stack repo for re-use. Other thing go into lab repos. Like the bunch of notebooks to do the wikipedia pageviews analysis.
There will be more info on how to make your own labs and, yes, the plugin thingy needs a bit more work before you can add your own repos, but it's very close and do make pull request.


# Included Labs
## Wikipedia Pageviews
Currently considered "done".
Documentation: https://github.com/jens-koster/the-free-data-stack/blob/main/docs/labs/wikipedia_pageviews.md

## JafKafe
In progress.
dbt jaffle shop generator as real time kafka event producer. Figuring the dbt models already provided will provide free wrok at the end of the pipeline.

Close, but not yet there


## Øresund Train Spotter
I've mothballed this to work on the JafKafe lab.

Repo: https://github.com/jens-koster/freeds-train-spotter

Project: https://github.com/users/jens-koster/projects/3


# create the root freeds folder
    After various attempts I came to the conclusion that we need a folder that can be on the same path in all of freeds, dockers, host, everything.
    Not including any current-user stuff, not a tmp folder that is magically recreated on restart. a simple persistent file folder for storing things...
    Especially spark is very finicky about...well everything, which includes folder locations.

    So, at least on mac you need to be root to create top level folders and then make yourself owner of that folder.

    sudo mkdir /opt/freeds
    sudo chown -R $USER:$USER /opt/freeds

    Docker desktop on mac protects the host by only allowing mounting on a few default folders like /tmp and ~, so you need to add /opt/freeds to the list in Settings->Resources->File sharing.

# plugin folder structure
Plugins reside in a repo, which has a git url.
Assumptions (to keep things simple):
* all repos are cloned to the same root dir, they need not be alone in it, but all are in the same directory.
* the git repo is cloned to a directory named as the repo, repo names are not required to be the same as the github repo names except for the core freeds repos. Allowing name clashes to be resolved in repos.yaml.
* plugins are in directories directly under a repo dir, one plugin in each directory. There can be other folders in the repo. (but plugin names are unique under the repo name)
* plugin directories are named after the plugin, plugin names are defined in config files. One config file per repo.
* There's a plugins.yaml config file that define the plugins in the-free-data-stack.
* *There's a repos.yaml defining the other plugin repos*
* there's a docker-compose.yaml file in every plugin directory
* there's a README.md in every plugin directory

How to find the roots:
*nyi: a ~/.freeds file is created poiting to a location for /opt/freeds and the full path to the folder with the repos.*
Default freeds searches the current directory and upwards to find the parent of 'the-free-data-stack' dir for repo root. It assumes '/opt/freeds' for the root of the app files.

# Networking

All docker compose files use a common network named `freeds-network`.
There's no "create if not exists" for networks in docker-compose so it needs to be created stand alone before firing up anything else. It is included in `setup.sh`

## port allocations
Port number mappings are kept globally unique, allowing us to run any ports of the stack together without port clashes.
All ports in docker shouare mapped to 127.0.0.1 on the host, to avoid exposing anything outside the local host.



## host mappings
Find out how to edit the hosts file on your os;

    # mac:
    sudo nano /etc/hosts



and add the following mappings:

    127.0.0.1 spark-master
    127.0.0.1 spark-worker-1
    127.0.0.1 spark-worker-2
    127.0.0.1 s3-minio
    127.0.0.1 freeds-config
    127.0.0.1 postgres
    127.0.0.1 devpi
    127.0.0.1 redisinsight
    127.0.0.1 redis
    127.0.0.1 airflow-webserver
    127.0.0.1 akhq
    127.0.0.1 kafdrop
    127.0.0.1 kafka-con-1
    127.0.0.1 kafka-bro-2
    127.0.0.1 kafka-brocon-3
    127.0.0.1 kafka-brocon-4

# Storage
Anything that can reasonably go on S3 shoud do so, we use minio S3 to provide a local (and free) S3 storage.
Sharing data on disk between dockers turned out not to solve all use cases. The airflow DockerOperator where you do "Docker in Docker", I could not get the spawned docker to mount a host directory. S3 and the config api server means we only need to supply the config server url to any docker in docker or host container. It is also easier editing a config on file and then directly using it in the code, rather than piping things thorugh env variables and whatnot. FREEDS is "opinionated", flexibility is traded for simplicity where it makes sense.

The default storage location root is ~/freeds, there is not yet an env variable to control the root. That will come...

S3 is first choice for any data shared between stack service.

We'll see what to do with DuckDB, you can create a readonly connection to it on s3. We could setup a duckdb container that performs the loading of the database and then publish it to s3 for readonly access...

postgreSQL uses a docker managed volume for storage.
