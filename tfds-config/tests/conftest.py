import os
import shutil
import tempfile

import pytest
from app import create_app


@pytest.fixture
def app():
    # Create a temporary directory for test YAML files
    test_data_dir = tempfile.mkdtemp()

    # Configure app to use the test directory
    os.environ["YAML_DATA_PATH"] = test_data_dir

    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app

    # Clean up the temporary directory
    shutil.rmtree(test_data_dir)


@pytest.fixture
def client(app):
    return app.test_client()
