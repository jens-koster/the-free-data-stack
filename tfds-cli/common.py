from pathlib import Path
import os
import yaml
TFDS_CONFIG_DIR = "./tfds-config/yaml_data"

def find_dir(dir_name: str) -> Path:
    """Find the specified directory in the current working directory or its parent directories."""
    looked_in = []
    p = Path(dir_name)
    # find repo and notebooks directories
    for i in range(4):
        looked_in.append(p.absolute())
        if p.exists():
            return p.absolute()
        p = Path("..") / p
    else:
        raise FileNotFoundError(
                f"Error: directory '{dir_name}' not found, looked in:\n{looked_in}"
            )


def get_config(config_name: str) -> dict:
    """Get the configuration from the specified YAML file."""

    config_file = Path(find_dir(TFDS_CONFIG_DIR)) / f"{config_name}.yaml"
    if not config_file.exists():
        print(f"Error: {config_file} does not exist.")
        return None

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    return config

def load_env_variables():
    """Load environment variables from YAML files in tfds-config/yaml_data.
    returns a dict of the added env variables."""
    if not Path(TFDS_CONFIG_DIR).exists():
        print(f"Warning: {TFDS_CONFIG_DIR} does not exist. Skipping environment variable setup.")
        return []
    envs =  {}
    for yaml_file in Path(TFDS_CONFIG_DIR).glob("*.yaml"):
        if yaml_file.name in ["stacks.yaml", "currentstack.yaml"]:
            continue
        base_name = yaml_file.stem.upper()
        complete_file = get_config(yaml_file.stem)
        if 'noenv' in complete_file.get('tfds-config', []):
            print(f"noenv set in {base_name} skipping it for env")
            continue
        config = complete_file.get('config', {})

        for key, value in config.items():
            if isinstance(value, list):
                value = ",".join(map(str, value))
            env_var = f"TFDS_{base_name}_{key.upper()}"
            os.environ[env_var] = str(value)
            envs[env_var] = str(value)

    return envs
if __name__ == '__main__':
    print(load_env_variables())