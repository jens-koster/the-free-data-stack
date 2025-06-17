# Lab repo layout
The only mandatory component of labs and plugins is the README.md in the root folder.
In general we don't like empty place holder folders, so create the ones you need and omit the others.

* If you have x-files in your lab, they should all be in the x directory.
* If you have no x-files, there should be no x directory.
* The x directory only contains x-files.

## Reserved folder names
### repo/config/
If you want to define one or more plugin stacks for your lab, you add a stacks.yaml in the config dir.
Any config for your local plugins go here as well, and gets served by the config server.

### repo/airflow/dags/
### repo/airflow/plugins/
If you use airflow this is where your dags and plugins go. (currently only dags will be supported We'll get to the airflow plugins folder and the others).
### repo/docs/
If you have more documentation than the root README.md it goes in the docs folder.
### repo/notebooks/
This is where your notebooks go, and get deployed to S# by the FreeDS CLI

### repo/plugins/
Lab local plugins go in the plugins folder, and get referrable from stacks.yaml.

## plugin folder structure
This is not rocket science, a plugin is always docker based. (current assumption)
Mandatory files are a README.md to descirbe the purpose and usage of the plugin and a docker-compose file for building build and running it.
repo/plugins/xxx/README.md
repo/plugins/xxx/docker-compose.yaml
