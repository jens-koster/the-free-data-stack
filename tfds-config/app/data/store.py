import fcntl  # For file locking to prevent race conditions
import os
from typing import Any, Dict, List, Optional

import yaml

CONFIG_PATH = "/app/config_files"
SECRETS_PATH = "/app/secret_files"

def format_response(path, name, notes, config):
    config = config.copy()
    config['meta'] =  {
            "name": name,
            "path": path,
            "notes": notes
        }
    return config

def strip_yaml(config_name)->str:
    if config_name.endswith(".yaml"):
        return config_name[:-5]
    if config_name.endswith(".yml"):
        return config_name[:-4]
    return config_name

def get_file_name(config_name):
    config_name = strip_yaml(config_name)
    attempt = os.path.join(SECRETS_PATH, config_name + '.yaml')
    if os.path.isfile(attempt):
        return attempt
    return os.path.join(CONFIG_PATH, config_name + '.yaml')


def read_config(config_name)-> dict:
    file_path = get_file_name(config_name)
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as file:
        config = yaml.safe_load(file) or {}

    return format_response(
        name=config_name,
        path=file_path,
        notes='loaded from disk',
        config=config
    )

def write_config(config_name: str, config_data: Dict) -> None:
    """Write a configuration file, the config is assumed to be the entire content."""
    file_path = get_file_name(config_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as file:
        # Lock the file to prevent race conditions
        fcntl.flock(file, fcntl.LOCK_EX)
        yaml.dump(config_data, file, default_flow_style=False)
        fcntl.flock(file, fcntl.LOCK_UN)


def delete_config(config_name: str) -> None:
    """Delete a configuration file."""
    file_path = get_file_name(config_name)
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print(f"Configuration '{file_path}' not found.")

def list_configs() -> List[str]:
    """List all available configuration files."""
    try:
        import os
        return [strip_yaml(f) for f in os.listdir(CONFIG_PATH)]
    except FileNotFoundError:
        return []
