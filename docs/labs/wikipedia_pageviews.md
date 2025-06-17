# Wikipedia page views data pipeline

## tldr:
Lab purpose is to mimic databricks.
The pipeline runs notebooks from airflow to download and process data in spark.

Wikipedia page view data is available for download as gzipped csv, one file per hour.

FreeDS stack: spark-stack

Airflow ELT pipeline: https://github.com/jens-koster/the-free-data-stack/blob/main/airflow/dags/dag_wikipedia_pageviews.py

Pipeline notebooks: https://github.com/jens-koster/pipe-dreams/tree/main/notebooks/wikipedia_pageviews

Note: If you let the airflow dag run on schedule the delta table will consume all your disk space.

## Rationale and description
This lab is for learning Databricks, so it's parameterized notebooks running in docker, a proper spark cluster in docker, delta tables on S3, and a catalog service (unity is proprietary, hive catalog service works but barely).
I wanted data with a lot of files, preferably provided more frequently than daily.
I wanted to build a pipeline in airflow, using the logical date and incremental loads in spark.

The bronze and silver layers are incrementally updated by reloading the last two days before leading up to the logical date.

The bronze and silver analyses are just what made sense from the available data, there's no real intention behind it.

S3 was chosen for technical reasons. Airflow in docker is spinning up the papermill contaier in docker to run the extract notebook. In this docker-in-docker situation there is no way to mount a local folder for sharing the downloaded data, so it needed to go somewhere online. Thus minio S3 was added as a plugin.

### Extract
Use papermill to run a parameterized notebook that downloads a configurable timespan of data files.
Each file is downloaded locally and then uploaded to S3.

### Bronze
Use spark to read the gzipped files, filter the content to a few countries where I know the language, add some meta data about the filename and clean out some wikipedia metadata etc.
Provide a date partitioned delta table on s3 with aggregated data on title, country, subdomain, date and number of views.
The delta table is incrementally updated for the two dates leading up to logical date.

### Silver
Use spark to read the delta table and provide an aggregate and ranking on date, country, and rank within the country and day.
The delta table is incrementally updated for the two dates leading up to logical date.

## Road map
This data should be visualised but I decided to leave that out of scope and move on to the next lab.

## Conclusions
It's interesting how the page of notable people who died ranks very hugh in every country.
