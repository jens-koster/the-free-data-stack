import fcntl  # For file locking to prevent race conditions
import os
from typing import Any, Dict, List, Optional

import yaml

DATA_PATH = os.environ.get("YAML_DATA_PATH", "/tmp/config")


def read_yaml(file_name: str) -> Dict:
    """Read data from a YAML file."""
    file_path = os.path.join(DATA_PATH, file_name)
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file) or {}
    except FileNotFoundError:
        return {}


def write_yaml(file_name: str, data: Dict) -> None:
    """Write data to a YAML file with file locking for thread safety."""
    file_path = os.path.join(DATA_PATH, file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as file:
        # Lock the file to prevent race conditions
        fcntl.flock(file, fcntl.LOCK_EX)
        yaml.dump(data, file, default_flow_style=False)
        fcntl.flock(file, fcntl.LOCK_UN)


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
