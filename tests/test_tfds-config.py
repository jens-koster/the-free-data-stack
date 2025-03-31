import requests
import os
from conftest import set_env_variables
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
        "doc": "this config is created by pytest and should be deleted",
        "config": {"test_value": "test_value"},
    }
    print('add config')
    response = requests.post(f"{os.environ[ENV_CONFIG]}/test_config", json=test_config)
    assert response.status_code == 201


    print('get config')
    response = requests.get(f"{os.environ[ENV_CONFIG]}/test_config")
    assert response.status_code == 200
    assert response.json()['config'] == test_config['config']
    assert response.json()['doc'] == test_config['doc']

    print('list config')
    response = requests.get(f"{os.environ[ENV_CONFIG]}/")
    assert response.status_code == 200
    assert "test_config" in response.json()["configs"]

    print('delete config')
    response = requests.delete(f"{os.environ[ENV_CONFIG]}/test_config")
    assert response.status_code == 204

def test_tfds_config():
    test_config = {
        "doc": "this config is created by pytest and should be deleted",
        "config": {"test_value": "test_value"},
        "tfds_config": []
    }

    response = requests.post(f"{os.environ[ENV_CONFIG]}/test_config", json=test_config)
    assert response.status_code == 201

    test_config['tfds_config'] = ['noenv']
    response = requests.post(f"{os.environ[ENV_CONFIG]}/test_config", json=test_config)
    assert response.status_code == 201

    response = requests.get(f"{os.environ[ENV_CONFIG]}/test_config")
    config = response.json()
    assert response.status_code == 200
    assert config.get('config') == test_config['config']
    assert config.get('doc') == test_config['doc']
    assert config.get('tfds_config') == test_config['tfds_config']

    test_config['tfds_config'] = ['noserve']
    response = requests.post(f"{os.environ[ENV_CONFIG]}/test_config", json=test_config)
    assert response.status_code == 400

    response = requests.delete(f"{os.environ[ENV_CONFIG]}/test_config")
    assert response.status_code == 204

if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__)+'/..')
    print(set_env_variables())

    test_tfds_config()
