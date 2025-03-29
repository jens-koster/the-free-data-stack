import fcntl  # For file locking to prevent race conditions
import os
from typing import Any, Dict, List, Optional

import yaml

DATA_PATH = os.environ.get("YAML_DATA_PATH", "/tmp/config")


def format_response(path, name, notes, config):
    return {
        "meta": {
            "name": name,
            "path": path,
            "notes": notes
        },
        "config": config
    }

def strip_yaml(config_name)->str:
    if config_name.endswith(".yaml"):
        return config_name[:-5]
    if config_name.endswith(".yml"):
        return config_name[:-4]
    return config_name


def get_file_name(config_name, must_exist=True):
    config_name = strip_yaml(config_name)
    file_path = os.path.join(DATA_PATH, config_name + '.yaml')
    if must_exist and not os.path.isfile(file_path):
        raise FileNotFoundError(f"Configuration file '{file_path}' not found.")
    return file_path


def read_config(config_name)-> dict:
    file_path = get_file_name(config_name)
    with open(file_path, "r") as file:
        config = yaml.safe_load(file) or {}

    return format_response(
        name=config_name,
        path=file_path,
        notes='loaded from disk',
        config=config
    )


def write_config(config_name: str, config: Dict) -> None:
    """write a config block, if config looks like a full response object the config element is extracted and the meta element is ignored.
    don't use the same names (meta and config) for an the actual config"""

    if 'meta' in  config.keys() and 'config' in config.keys() and len(config.keys())==2:
        #we likely have a full response object, let's strip the config part.
        config = config['config']
    file_path = get_file_name(config_name, must_exist=False)
    write_yaml(file_path=file_path, data=config)

def write_yaml(file_path: str, data: Dict) -> None:
    """Write data to a YAML file with file locking for thread safety."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as file:
        # Lock the file to prevent race conditions
        fcntl.flock(file, fcntl.LOCK_EX)
        yaml.dump(data, file, default_flow_style=False)
        fcntl.flock(file, fcntl.LOCK_UN)

def delete_config(config_name: str) -> None:
    """Delete a configuration file."""
    file_path = get_file_name(config_name, must_exist=False)
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print(f"Configuration '{file_path}' not found.")

def list_configs() -> List[str]:
    """List all available configuration files."""
    try:
        import os

        print(os.path.abspath(DATA_PATH))
        print([f for f in os.listdir(DATA_PATH)])
        return [f for f in os.listdir(DATA_PATH)]
    except FileNotFoundError:
        os.makedirs(DATA_PATH, exist_ok=True)
        return []
