import requests
import os

ENV_CONFIG = 'TFDS_CONFIG_URL'


def test_list_configs_non_empty():
    print('*'*80)
    print(os.environ[ENV_CONFIG])
    print('*'*80)
    response = requests.get(f"{os.environ[ENV_CONFIG]}/")
    assert response.status_code == 200
    assert len(response.json()["configs"]) > 0

# todo add logging in the config service

def test_create_and_get_config():
    # Create a new config
    test_config = {
        "annotation": "test_annotation",
        "config": {"test_value": "test_value"},
    }
    print('add config')
    response = requests.post(f"{os.environ[ENV_CONFIG]}/test_config", json=test_config)
    assert response.status_code == 201


    print('get config')
    response = requests.get(f"{os.environ[ENV_CONFIG]}/test_config")
    assert response.status_code == 200
    assert response.get_json() == test_config

    print('list config')
    response = requests.get(f"{os.environ[ENV_CONFIG]}/")
    assert response.status_code == 200
    assert "test_config.yaml" in response.get_json()["configs"]

    print('delete config')
    response = requests.delete(f"{os.environ[ENV_CONFIG]}/test_config")
    assert response.status_code == 204
