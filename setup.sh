#!/bin/bash

# we need a common network so the containers can communicate
# this is  persistent so no need to run this command but once.
echo "creating docker tfds-network..."
output=$(docker network create tfds-network 2>&1)
if [[ "$output" == *"Error response from daemon: network with name tfds-network already exists"* ]]; then
    echo "tfds-network already exists, if you need it recreated run "docker network rm tfds-network" and then run this script again"
else
    echo "$output"
fi

root=/opt/tfds




mkdir -p "$root"/airflow
mkdir -p "$root"/logs
mkdir -p "$root"/data
mkdir -p "$root"/spark
mkdir -p "$root"/data/minio
mkdir -p "$root"/data/spark-warehouse
mkdir -p "$root"/data/spark
mkdir -p "$root"/data/spark/metastore


# spark
echo "linking spark conf and jars folders to $root/spark"
if [ -L "$root"/spark/jars ]; then
    rm "$root"/spark/jars
fi
ln -s "$(pwd)/spark/jars" "$root"/spark/jars


if [ -L "$root"/spark/jars ]; then
    rm "$root"/spark/conf
fi
ln -s "$(pwd)/spark/conf" "$root"/spark/conf


# tfds
echo "linking config folder to $root/config"

if [ -L "$root"/config ]; then
    rm "$root"/config
fi
ln -s "$(pwd)/tfds-config/yaml_data" "$root"/config


echo "Creating secrets fodler and copying content: $root/sercrets"
mkdir -p "$root"/secrets
cp -rn "./tfds-config/secret_data/"* "$root"/secrets

# Airflow
echo "linking some airflow folders"
if [ -L "$root"/airflow/config ]; then
    rm "$root"/airflow/config
fi
ln -s "$(pwd)/airflow/config" "$root"/airflow/config

if [ -L "$root"/airflow/plugins ]; then
    rm "$root"/airflow/plugins
fi
ln -s "$(pwd)/airflow/plugins" "$root"/airflow/plugins

if [ -L "$root"/airflow/dags ]; then
    rm "$root"/airflow/dags
fi
ln -s "$(pwd)/airflow/dags" "$root"/airflow/dags

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
        pip install -r ./spark/requirements.txt
    else
        echo "Skipping venv creation, here's the DYI version:"
        echo ""
        echo "python3 -m venv .venv"
        echo "source .venv/bin/activate"
        echo "pip install --upgrade pip"
        echo "pip install -r requirements.txt"
        echo "pip install -r ./spark/requirements.txt"
    fi
fi
