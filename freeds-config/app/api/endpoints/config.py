from typing import Any

from app.api.schemas.request_models import ConfigFileSchema
from app.api.schemas.response_models import (
    ConfigFileResponseSchema,
    ConfigListResponseSchema,
)
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from freeds.config.file import (
    delete_config,
    list_configs,
    read_config,
    write_config_to_file,
)

blp = Blueprint(
    "Configurations",
    __name__,
    description="Operations on TFDS configurations",
    url_prefix="/api/configs",
)


def is_served(config_name: str) -> bool:
    data = read_config(config_name)
    if data is None:
        return True
    return "noserve" not in data.get("tfds_config", [])


def printlog() -> None:
    print("#" * 20, request.method, request.path)


@blp.route("/")
class ConfigList(MethodView):  # type: ignore[misc]
    @blp.response(200, ConfigListResponseSchema)  # type: ignore[misc]
    def get(self) -> dict[str, Any]:
        printlog()
        """List all served configuration files"""
        config_files = [c for c in list_configs() if is_served(c)]
        return {"configs": config_files}


@blp.route("/<string:config_name>")
class ConfigResource(MethodView):  # type: ignore[misc]
    @blp.response(200, ConfigFileResponseSchema)  # type: ignore[misc]
    @blp.response(404)  # type: ignore[misc]
    def get(self, config_name: str) -> tuple[dict[str, Any], int]:
        """Retrieve a configuration file"""
        printlog()
        if not is_served(config_name):
            abort(404, message=f"Configuration '{config_name}' not found")
        data = read_config(config_name)
        if data is None:
            abort(404, message=f"Configuration '{config_name}' not found")
        return data, 200

    @blp.arguments(ConfigFileSchema)  # type: ignore[misc]
    @blp.response(201, ConfigFileResponseSchema)  # type: ignore[misc]
    def post(self, config_data: dict[str, Any], config_name: str) -> tuple[dict[str, Any], int]:
        """Create or update a configuration file"""
        printlog()
        if not is_served(config_name):
            abort(400, message=f"Permission denied, '{config_name}' is not served through the api.")
        if "noserve" in config_data.get("tfds_config", []):
            abort(
                400,
                message="Permission denied, can't save 'noserve' configs thourgh the api, that would be non reversible.",
            )
        write_config_to_file(config_name=config_name, config_data=config_data)
        return read_config(config_name), 201

    @blp.response(204)  # type: ignore[misc]
    def delete(self, config_name: str) -> tuple[str, int]:
        """Delete a configuration file"""
        printlog()
        if not is_served(config_name):
            abort(400, message=f"Permission denied, '{config_name}' is not served through the api.")
        delete_config(config_name)
        return "", 204
