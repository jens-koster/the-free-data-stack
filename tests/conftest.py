import os
import subprocess
import pytest


def set_env_variables():
    """Run tfds-cli to set environment variables for all tests."""

    try:
        # Run the tfds-cli command and capture its output
        result = subprocess.run(
            ["python3", "./tfds-cli/tfds.py", "env"],
            check=True,
            text=True,
            capture_output=True,
        )
        print("Setting up env")
        # Parse the output and set environment variables in the parent process
        for line in result.stdout.splitlines():
            if line.startswith("TFDS_") and '=' in line:  # Ensure the line contains an environment variable
                key, value = line.split("=", 1)
                os.environ[key] = value
        # set some hardcoded values where we want to access 127.0.0.1 rather than the docker network host name
        os.environ['TFDS_CONFIG_URL']='http://127.0.0.1:8005/api/configs'
        for key, value in os.environ.items():
            if key.startswith("TFDS_"):
                print(f"{key}={value}")
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Failed to run tfds-cli: {e}\n{e.stderr}\n{e.stdout}")


@pytest.fixture(scope="session", autouse=True)
def setup_env_variables():
    set_env_variables()

# @pytest.fixture(scope="session", autouse=True)
# def start_stack(setup_env_variables):
#     try:
#         # Run the tfds-cli command and capture its output
#         print("Stopping the stack (in case it is running)")
#         subprocess.run(
#             ["python3", "./tfds-cli/tfds.py", "down"],
#             check=True,
#             text=True,
#         )
#         print("Building the stack")
#         subprocess.run(
#             ["python3", "./tfds-cli/tfds.py", "build"],
#             check=True,
#             text=True,
#         )
#         print("Starting the stack")
#         subprocess.run(
#             ["python3", "./tfds-cli/tfds.py", "up"],
#             check=True,
#             text=True,
#         )
#         yield
#     except subprocess.CalledProcessError as e:
#         pytest.fail(f"Failed to run tfds-cli: {e}\n{e.stderr}\n{e.stdout}")
#     finally:
#         print("Stopping the stack")
#         subprocess.run(
#             ["python3", "./tfds-cli/tfds.py", "down"],
#             check=True,
#             text=True,
#         )
#         print("Removing the stack")
#         subprocess.run(
#             ["python3", "./tfds-cli/tfds.py", "rm"],
#             check=True,
#             text=True,
#         )



if __name__ == '__main__':
    set_env_variables()