# TFDS-Config Service

A simple API server for managing YAML-based configuration files.

## Overview

TFDS-Config provides a RESTful API for creating, reading, updating, and deleting configuration files stored in YAML format. It's built using Flask and OpenAPI/Swagger for documentation.

## Features

- CRUD operations for configuration files
- Automatic API documentation via Swagger UI and ReDoc
- Docker containerization for easy deployment
- YAML-based storage with file locking for concurrent access



The API will be available at:
- http://localhost:8005/api/configs/
- http://localhost:8005/swagger-ui (API documentation)
- http://localhost:8005/redoc (Alternative API documentation)

### API Endpoints

- `GET /api/configs/` - List all configuration files
- `GET /api/configs/{config_name}` - Get a specific configuration
- `POST /api/configs/{config_name}` - Create or update a configuration
- `DELETE /api/configs/{config_name}` - Delete a configuration
