## papermill service
papermill is a tool for running parameterized notebooks: https://papermill.readthedocs.io/en/latest/

papermill takes a notebook, parameters and an output filename.
It runs the notebook and stores the resulting notebook at the specified location, i.e. the original notebook is not modified.

tfds papermill service is intended for use with airflow DockerOperator.
It seems impossible to mount a host folder through the DockerOperator while airflow itself is also running in docker. (docker-in-docker) At least in a mac. So, I moved to S3, which also seems more production like. Notebooks and output notebooks are now on S3.
