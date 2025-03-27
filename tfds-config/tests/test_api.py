def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_list_configs_empty(client):
    response = client.get("/api/configs/")
    assert response.status_code == 200
    assert response.get_json() == {"configs": []}


def test_create_and_get_config(client):
    # Create a new config
    test_config = {
        "name": "test_config",
        "items": [{"name": "test_param", "value": 42, "description": "Test parameter"}],
    }

    response = client.post("/api/configs/test_config", json=test_config)
    assert response.status_code == 201

    # Get the config
    response = client.get("/api/configs/test_config")
    assert response.status_code == 200
    assert response.get_json() == test_config

    # List configs should now show our config
    response = client.get("/api/configs/")
    assert response.status_code == 200
    assert "test_config.yaml" in response.get_json()["configs"]

    # Delete the config
    response = client.delete("/api/configs/test_config")
    assert response.status_code == 204
