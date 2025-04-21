#!/usr/bin/env python3
import os
import sys
import yaml
import subprocess
from pathlib import Path
from common import load_env_variables, get_config_file
from s3 import create_s3_bucket


STACKS_FILE = get_config_file("stacks")
CURRENT_STACK_FILE = get_config_file("currentstack")


def load_stacks()->dict:
    """Load the stacks from the stacks.yaml file."""
    if not STACKS_FILE.exists():
        print(f"Error: {STACKS_FILE} does not exist.")
        return None

    with open(STACKS_FILE, "r") as f:
        stacks = yaml.safe_load(f)
    return stacks['config']


def init():
    """
        Create the stacks.yaml file if it doesn't exist and populate it with sample content.
        creates the buckets if they don't exist.

    """
    if not STACKS_FILE.exists():
        sample_content = {
            'annotation': 'The stack definitions for tfds cli. tfds will do some magic and then iterate these folders in order to run docker compose with the chosen command in each',
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
        if get_current_stack() is None:
            stacks = load_stacks()
            set_current_stack(stacks.keys()[0])
    create_s3_bucket("notebooks")
    create_s3_bucket("output-notebooks")
    create_s3_bucket("data")
    create_s3_bucket("dwh")


def get_current_stack()->str:
    """Get the current stack name from the currentstack.yaml file."""
    if not CURRENT_STACK_FILE.exists():
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
            print(f"Running 'docker compose {command}' for service '{svc}' {args}...")
            cmd = ["docker", "compose", command, *args]
            if command in ["up", "start"]:
                cmd.append("-d")
            print(os.getcwd(), cmd)
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to execute 'docker compose {command}' for service '{svc}'.")
            return 1
        finally:
            os.chdir(start_dir)


def main():
    if len(sys.argv) < 2:
        print("Usage: tfds.py <command> [options]")
        print("options are passed on docker compose except -s <service> which executes the docker command for one service.")
        print("Commands: init, ls, setstack <stack_name>, <docker_compose_command>")
        print(sys.argv)
        return 1

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
        envs = load_env_variables()
        print( '\n'.join(f'export {key}={value}' for key, value in envs.items() ))

    elif command == "setstack":
        if len(sys.argv) < 3:
            print("Usage: tfds.py setstack <stack_name>")
            sys.exit(1)
        set_current_stack(sys.argv[2])

    else:
        # any docker compose command is allowed, let docker compose print any errors...
        is_service_seq = False
        service = None
        args = []
        for arg in sys.argv[2:]:
            if is_service_seq:
                service = arg
                is_service_seq = False
            elif arg == '-s':
                is_service_seq = True
            else:
                args.append(arg)
        execute_docker_command(command, service, *args)

    os.chdir(start_dir)


if __name__ == "__main__":
    main()
