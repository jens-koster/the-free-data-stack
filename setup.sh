#!/bin/bash

# globals
mkdir -p /tmp

# a folder where all logs are stores
mkdir -p /tmp/logs

# we need a common network so the containers can communicate
# this is  persistent so no need to run this command but once.

echo "creating docker tfds-network..."
output=$(docker network create tfds-network 2>&1)
if [[ "$output" == *"Error response from daemon: network with name tfds-network already exists"* ]]; then
    echo "tfds-network already exists, if you need it recreated run "docker network rm tfds-network" and then run this script again"
else
    echo "$output"
fi

echo "creating folders in /tmp and link some folders from the project to /tmp"
# link the data folder in a well known location, probabaly won't be needing this when all is using s3-ninja
echo "linking _data folder to /tmp/data"
if [ -L /tmp/data ]; then
    rm /tmp/data
fi
ln -s "$(pwd)/_data" /tmp/data

# tfds
echo "linking config folder to /tmp/tfds/config"
mkdir -p /tmp/tfds
if [ -L /tmp/tfds/config ]; then
    rm /tmp/tfds/config
fi
ln -s "$(pwd)/tfds-config/yaml_data" /tmp/tfds/config

# Airflow
echo "linking some airflow folders to /tmp/tfds/airflow/*"
mkdir -p /tmp/logs/airflow
mkdir -p /tmp/airflow

if [ -L /tmp/airflow/config ]; then
    rm /tmp/airflow/config
fi
ln -s "$(pwd)/Airflow/config" /tmp/airflow/config

if [ -L /tmp/airflow/plugins ]; then
    rm /tmp/airflow/plugins
fi
ln -s "$(pwd)/Airflow/plugins" /tmp/airflow/plugins

if [ -L /tmp/airflow/dags ]; then
    rm /tmp/airflow/dags
fi
ln -s "$(pwd)/Airflow/dags" /tmp/airflow/dags

echo "setting up python..."
echo "making sure there's a venv and that it's activated..."
venv_activate=$(find . -type f -path "./*/bin/activate" -depth 3 | head -n 1)

if [ -n "$venv_activate" ]; then
    echo "Found existing virtual environment, activating it: $venv_activate"
    source "$venv_activate"
else
    echo "No virtual environment found."

    echo "Would you like to create a venv and install requirements.txt? (y/n): "
    read create_venv
    if [[ "$create_venv" =~ ^[Yy]$ ]]; then
        echo "Creating venv '.venv'"
        python3 -m venv .venv
        source .venv/bin/activate
        echo "Virtual environment .venv created and activated."
        echo "Upgrading pip and installing requirements..."
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        echo "Skipping venv creation, here's the DYI version:"
        echo ""
        echo "python3 -m venv .venv"
        echo "source .venv/bin/activate"
        echo "pip install --upgrade pip"
        echo "pip install -r requirements.txt"
    fi
fi
