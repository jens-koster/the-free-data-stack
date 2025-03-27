I'll create a shell script that will set up the entire project structure for your `tfds-config` service, including creating the necessary directories and files with the suggested content.

```bash
#!/bin/bash

# Create the main project directory
mkdir -p tfds-config
cd tfds-config

# Create the app directory structure
mkdir -p app/api/endpoints app/api/schemas app/core app/data/data_files app/services

# Create the tests directory
mkdir -p tests

# Create __init__.py files
touch app/__init__.py
touch app/api/__init__.py
touch app/api/endpoints/__init__.py
touch app/api/schemas/__init__.py
touch app/core/__init__.py
touch app/data/__init__.py
touch app/services/__init__.py
touch tests/__init__.py

# Create main app/__init__.py with Flask app factory
cat > app/__init__.py << 'EOF'
from flask import Flask
from flask_smorest import Api

def create_app():
    app = Flask(__name__)

    # Configure OpenAPI documentation
    app.config["API_TITLE"] = "TFDS-Config API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["OPENAPI_REDOC_PATH"] = "/redoc"
    app.config["OPENAPI_REDOC_URL"] = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"

    api = Api(app)

    # Register blueprints
    from app.api.endpoints.config import blp as config_blueprint

    api.register_blueprint(config_blueprint)

    @app.route('/health')
    def health_check():
        return {"status": "healthy"}, 200

    return app
EOF

# Create core/config.py
cat > app/core/config.py << 'EOF'
import os

class Config:
    # API configuration
    API_TITLE = "TFDS-Config API"
    API_VERSION = "v1"

    # YAML data path
    YAML_DATA_PATH = os.environ.get('YAML_DATA_PATH', 'app/data/data_files')

    # JWT configuration (if needed)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')

    # Environment-specific configs can be added here
    @classmethod
    def get_config(cls):
        env = os.environ.get('FLASK_ENV', 'development')
        if env == 'production':
            return ProductionConfig
        elif env == 'testing':
            return TestingConfig
        return DevelopmentConfig

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
EOF

# Create data/store.py for YAML handling
cat > app/data/store.py << 'EOF'
import yaml
import os
import fcntl  # For file locking to prevent race conditions
from typing import Dict, List, Any, Optional

DATA_PATH = os.environ.get('YAML_DATA_PATH', 'app/data/data_files')

def read_yaml(file_name: str) -> Dict:
    """Read data from a YAML file."""
    file_path = os.path.join(DATA_PATH, file_name)
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file) or {}
    except FileNotFoundError:
        return {}

def write_yaml(file_name: str, data: Dict) -> None:
    """Write data to a YAML file with file locking for thread safety."""
    file_path = os.path.join(DATA_PATH, file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w') as file:
        # Lock the file to prevent race conditions
        fcntl.flock(file, fcntl.LOCK_EX)
        yaml.dump(data, file, default_flow_style=False)
        fcntl.flock(file, fcntl.LOCK_UN)

def list_configs() -> List[str]:
    """List all available configuration files."""
    try:
        return [f for f in os.listdir(DATA_PATH) if f.endswith('.yaml')]
    except FileNotFoundError:
        os.makedirs(DATA_PATH, exist_ok=True)
        return []
EOF

# Create schema files
cat > app/api/schemas/request_models.py << 'EOF'
from marshmallow import Schema, fields, validate

class ConfigItemSchema(Schema):
    """Schema for a configuration item."""
    name = fields.Str(required=True, description="Configuration name")
    value = fields.Raw(required=True, description="Configuration value (can be any type)")
    description = fields.Str(description="Description of this configuration")

    class Meta:
        description = "A single configuration item"
        example = {
            "name": "max_batch_size",
            "value": 64,
            "description": "Maximum batch size for processing"
        }

class ConfigFileSchema(Schema):
    """Schema for a complete configuration file."""
    name = fields.Str(required=True, description="Configuration file name")
    items = fields.List(fields.Nested(ConfigItemSchema), required=True)

    class Meta:
        description = "A configuration file with multiple items"
        example = {
            "name": "training_config",
            "items": [
                {
                    "name": "max_batch_size",
                    "value": 64,
                    "description": "Maximum batch size for processing"
                },
                {
                    "name": "learning_rate",
                    "value": 0.001,
                    "description": "Learning rate for optimizer"
                }
            ]
        }
EOF

cat > app/api/schemas/response_models.py << 'EOF'
from marshmallow import Schema, fields
from app.api.schemas.request_models import ConfigItemSchema, ConfigFileSchema

# Reuse the request schemas for responses where appropriate
ConfigItemResponseSchema = ConfigItemSchema
ConfigFileResponseSchema = ConfigFileSchema

class ConfigListResponseSchema(Schema):
    """Schema for listing available configuration files."""
    configs = fields.List(fields.Str(), description="List of available configuration files")

    class Meta:
        description = "List of available configuration files"
        example = {
            "configs": ["training_config.yaml", "preprocessing_config.yaml"]
        }

class ErrorResponseSchema(Schema):
    """Schema for error responses."""
    message = fields.Str(required=True, description="Error message")
    status_code = fields.Int(required=True, description="HTTP status code")

    class Meta:
        description = "Error response"
        example = {
            "message": "Configuration file not found",
            "status_code": 404
        }
EOF

# Create endpoint file
cat > app/api/endpoints/config.py << 'EOF'
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.api.schemas.request_models import ConfigItemSchema, ConfigFileSchema
from app.api.schemas.response_models import (
    ConfigItemResponseSchema,
    ConfigFileResponseSchema,
    ConfigListResponseSchema
)
from app.data.store import read_yaml, write_yaml, list_configs

blp = Blueprint(
    "Configurations",
    __name__,
    description="Operations on TFDS configurations",
    url_prefix="/api/configs"
)

@blp.route("/")
class ConfigList(MethodView):
    @blp.response(200, ConfigListResponseSchema)
    def get(self):
        """List all available configuration files"""
        config_files = list_configs()
        return {"configs": config_files}

@blp.route("/<string:config_name>")
class ConfigResource(MethodView):
    @blp.response(200, ConfigFileResponseSchema)
    @blp.response(404)
    def get(self, config_name):
        """Get a specific configuration file"""
        # Ensure .yaml extension
        if not config_name.endswith(".yaml"):
            config_name += ".yaml"

        data = read_yaml(config_name)
        if not data:
            abort(404, message=f"Configuration '{config_name}' not found")

        return {"name": config_name.replace(".yaml", ""), "items": data.get("items", [])}

    @blp.arguments(ConfigFileSchema)
    @blp.response(201, ConfigFileResponseSchema)
    def post(self, config_data, config_name):
        """Create or update a configuration file"""
        # Ensure .yaml extension
        if not config_name.endswith(".yaml"):
            config_name += ".yaml"

        write_yaml(config_name, {"items": config_data["items"]})
        return {"name": config_name.replace(".yaml", ""), "items": config_data["items"]}, 201

    @blp.response(204)
    @blp.response(404)
    def delete(self, config_name):
        """Delete a configuration file"""
        # Ensure .yaml extension
        if not config_name.endswith(".yaml"):
            config_name += ".yaml"

        import os
        from app.data.store import DATA_PATH

        file_path = os.path.join(DATA_PATH, config_name)
        if not os.path.exists(file_path):
            abort(404, message=f"Configuration '{config_name}' not found")

        os.remove(file_path)
        return "", 204
EOF

# Create service logic stub
cat > app/services/business_logic.py << 'EOF'
# This file can contain any business logic for your application
# For example, validation, transformation, or complex operations on your YAML data

def validate_config(config_data):
    """Placeholder for config validation logic."""
    # Example: check for required keys, value types, etc.
    return True

def transform_config(config_data):
    """Placeholder for config transformation logic."""
    # Example: convert units, normalize values, etc.
    return config_data
EOF

# Create WSGI entry point
cat > wsgi.py << 'EOF'
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
EOF

# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a volume for YAML data files
VOLUME /app/app/data/data_files

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
EOF

# Create docker-compose.yaml
cat > docker-compose.yaml << 'EOF'
version: '3.8'

services:
  api:
    build: .
    image: tfds-config
    container_name: tfds-config
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - YAML_DATA_PATH=/app/app/data/data_files
    volumes:
      - yaml_data:/app/app/data/data_files

volumes:
  yaml_data:
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
Flask==2.2.3
flask-smorest==0.41.0
marshmallow==3.19.0
PyYAML==6.0
pytest==7.2.2
gunicorn==20.1.0
EOF

# Create test files
cat > tests/conftest.py << 'EOF'
import pytest
from app import create_app
import os
import tempfile
import shutil

@pytest.fixture
def app():
    # Create a temporary directory for test YAML files
    test_data_dir = tempfile.mkdtemp()

    # Configure app to use the test directory
    os.environ['YAML_DATA_PATH'] = test_data_dir

    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    yield app

    # Clean up the temporary directory
    shutil.rmtree(test_data_dir)

@pytest.fixture
def client(app):
    return app.test_client()
EOF

cat > tests/test_api.py << 'EOF'
def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}

def test_list_configs_empty(client):
    response = client.get('/api/configs/')
    assert response.status_code == 200
    assert response.get_json() == {"configs": []}

def test_create_and_get_config(client):
    # Create a new config
    test_config = {
        "name": "test_config",
        "items": [
            {
                "name": "test_param",
                "value": 42,
                "description": "Test parameter"
            }
        ]
    }

    response = client.post('/api/configs/test_config', json=test_config)
    assert response.status_code == 201

    # Get the config
    response = client.get('/api/configs/test_config')
    assert response.status_code == 200
    assert response.get_json() == test_config

    # List configs should now show our config
    response = client.get('/api/configs/')
    assert response.status_code == 200
    assert "test_config.yaml" in response.get_json()["configs"]

    # Delete the config
    response = client.delete('/api/configs/test_config')
    assert response.status_code == 204
EOF

# Create README.md
cat > README.md << 'EOF'
# TFDS-Config Service

A simple API server for managing YAML-based configuration files.

## Overview

TFDS-Config provides a RESTful API for creating, reading, updating, and deleting configuration files stored in YAML format. It's built using Flask and OpenAPI/Swagger for documentation.

## Features

- CRUD operations for configuration files
- Automatic API documentation via Swagger UI and ReDoc
- Docker containerization for easy deployment
- YAML-based storage with file locking for concurrent access
- Health check endpoint

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Running the service

```bash
docker-compose up -d
```

The API will be available at:
- http://localhost:5000/api/configs/
- http://localhost:5000/swagger-ui (API documentation)
- http://localhost:5000/redoc (Alternative API documentation)

### API Endpoints

- `GET /api/configs/` - List all configuration files
- `GET /api/configs/{config_name}` - Get a specific configuration
- `POST /api/configs/{config_name}` - Create or update a configuration
- `DELETE /api/configs/{config_name}` - Delete a configuration

## Development

### Running tests

```bash
pip install -r requirements.txt
pytest
```

### Local development

```bash
pip install -r requirements.txt
export FLASK_ENV=development
python wsgi.py
```
EOF

# Make the script executable
chmod +x wsgi.py

echo "TFDS-Config project structure has been successfully created!"
echo "To start the service, run: docker-compose up -d"
echo "The API documentation will be available at: http://localhost:5000/swagger-ui"

```

This script will create a full project structure for your `tfds-config` service with all the files and content as discussed. Here's what it does:

1. Creates the entire directory structure
2. Populates all the files with recommended content:
   - Flask application with flask-smorest for OpenAPI documentation
   - YAML-based data storage with file locking for thread safety
   - RESTful API endpoints for managing configuration files
   - Marshmallow schemas for request/response validation
   - Docker and Docker Compose configuration
   - Basic test setup with pytest

To use this script:

1. Save it to a file (e.g., `setup-tfds-config.sh`)
2. Make it executable: `chmod +x setup-tfds-config.sh`
3. Run it: `./setup-tfds-config.sh`

After running the script, you'll have a complete, ready-to-run API service that:
- Stores configuration data in YAML files
- Provides RESTful endpoints for managing configurations
- Includes interactive API documentation with Swagger UI and ReDoc
- Is containerized with Docker for easy deployment
- Has test scaffolding for adding unit tests

You can start the service with `docker-compose up -d` and access the API documentation at `http://localhost:5000/swagger-ui`.