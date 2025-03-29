#!/usr/bin/env python3
import os
import sys
import yaml
import subprocess
from pathlib import Path

TFDS_CLI_FOLDER = Path(__file__).resolve().parent  # Get the directory of the current file

TFDS_CONFIG_DIR = "tfds-config/yaml_data"
STACKS_FILE = f"{TFDS_CONFIG_DIR}/stacks.yaml"
CURRENT_STACK_FILE = f"{TFDS_CONFIG_DIR}/currentstack.yaml"


def load_stacks()->dict:
    """Load the stacks from the stacks.yaml file."""
    if not Path(STACKS_FILE).exists():
        print(f"Error: {STACKS_FILE} does not exist.")
        return None

    with open(STACKS_FILE, "r") as f:
        stacks = yaml.safe_load(f)
    return stacks['config']


def init():
    """Create the stacks.yaml file if it doesn't exist and populate it with sample content."""
    if not Path(STACKS_FILE).exists():
        sample_content = {
            'config': {
                'spark-stack': {'services': ['tfds-config', 's3-ninja', 'postgreSQL', 'spark', 'papermill', 'airflow']},
                'x-stack': {'services': ['tfds-config', 's3-ninja', 'clickhouse']}
                }
            }
        with open(STACKS_FILE, "w") as f:
            yaml.dump(sample_content, f)
        print(f"{STACKS_FILE} created with sample content.")
        set_current_stack('spark-stack')
    else:
        print(f"{STACKS_FILE} already exists.")


def get_current_stack()->str:
    """Get the current stack name from the currentstack.yaml file."""
    if not Path(CURRENT_STACK_FILE).exists():
        print(f"Error: {CURRENT_STACK_FILE} does not exist.")
        return None

    with open(CURRENT_STACK_FILE, "r") as f:
        current_stack = yaml.safe_load(f)
    return current_stack['config'].get('current_stack', None)


def set_current_stack(stack_name):
    stack_names=load_stacks().keys()
    if stack_name not in stack_names:
        print(f"Error: Stack '{stack_name}' not found in {STACKS_FILE}.")
        print(f"Available stacks: {', '.join(stack_names)}")
        return

    with open(CURRENT_STACK_FILE, "w") as file:
        # Lock the file to prevent race conditions
        config = {
            'annotation': 'the current stack for tfds cli, use setstack to change it, editing here is fine too',
            'config': {
                'current_stack': stack_name}
                }
        yaml.dump(config, file, default_flow_style=False)
    print(f"Current stack set to '{stack_name}'.")


def load_env_variables():
    """Load environment variables from YAML files in tfds-config/yaml_data."""
    if not Path(TFDS_CONFIG_DIR).exists():
        print(f"Warning: {TFDS_CONFIG_DIR} does not exist. Skipping environment variable setup.")
        return

    for yaml_file in Path(TFDS_CONFIG_DIR).glob("*.yaml"):
        if yaml_file.name in ["stacks.yaml", "currentstack.yaml"]:
            continue
        with open(yaml_file, "r") as f:
            config = yaml.safe_load(f)
        base_name = yaml_file.stem.upper()
        config = config.get('config', {})
        for key, value in config.items():
            env_var = f"TFDS_{base_name}_{key.upper()}"
            os.environ[env_var] = str(value)


def execute_docker_command(command, service=None, *args):
    """Execute a Docker Compose command for the current stack."""
    current_stack = get_current_stack()
    stack_services=[]
    if service:
        stack_services = [service]
    else:
        stacks = load_stacks()
        if current_stack not in stacks:
            print(f"Error: Stack '{current_stack}' not found in {STACKS_FILE}.")
            return 1
        stack_services = stacks[current_stack].get('services',[])

        if command in ["down", "stop"]:
            stack_services =  reversed(stack_services)

    # Load environment variables
    load_env_variables()

    # Execute the command for each service
    start_dir = os.getcwd()
    for svc in stack_services:
        service_dir = Path(start_dir) / svc
        if not service_dir.exists():
            print(f"Warning: Service directory '{service_dir}' does not exist. Skipping.")
            continue

        os.chdir(service_dir)
        try:
            print(f"Running 'docker compose {command}' for service '{svc}'...")
            subprocess.run(["docker", "compose", command, *args], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to execute 'docker compose {command}' for service '{svc}'.")
            sys.exit(1)
        finally:
            os.chdir(start_dir)


def main():
    if len(sys.argv) < 2:
        print("Usage: stack_manager.py <command> [options]")
        print("options are passed on docker compose except -s <service> which executes the docker command for one service.")
        print("Commands: init, ls, setstack <stack_name>, <docker_compose_command>")
        sys.exit(1)

    start_dir = Path.cwd()  # Get the current working directory and make sure we end up back there
    # Check if we're in a project subdirectory and move to root if necessary
    parent_dir = start_dir.parent
    if (parent_dir / "tfds-cli").is_dir():
        os.chdir(parent_dir)

    command = sys.argv[1]
    if command == "init":
        init()
    elif command == "ls":
        print ('\n' + '='*20 + ' stacks ' + '='*20)
        stacks = load_stacks()
        if stacks:
            for stack_name, stack in stacks.items():
                print(f"- {stack_name}: {', '.join(stack['services'])}")
        else:
            print("No stacks found.")
    elif command == "env":
        print ('\n' + '='*20 + ' TFDS env variables ' + '='*20)
        load_env_variables()
        result = subprocess.run("env | grep TFDS", shell=True, text=True, capture_output=True)
        if result.returncode == 0:
            print(result.stdout)  # Print the matched environment variables
        else:
            print("No matching environment variables found.")

    elif command == "setstack":
        if len(sys.argv) < 3:
            print("Usage: tfds.py setstack <stack_name>")
            sys.exit(1)
        set_current_stack(sys.argv[2])

    else:
        # any docker compose command is allowed, let docker compose print any errors...
        service = None
        args = []
        for arg in sys.argv[2:]:
            if is_service:
                service = arg
                is_service = False
            elif arg == '-s':
                is_service = True
            else:
                args.append(arg)
        execute_docker_command(command, service, *args)

    os.chdir(start_dir)

if __name__ == "__main__":
    main()
