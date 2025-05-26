from app.api.schemas.request_models import ConfigFileSchema
from app.api.schemas.response_models import (
    ConfigFileResponseSchema,
    ConfigListResponseSchema,
)
from tfdslib.config_file import list_configs, read_config, write_config_to_file, delete_config
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint(
    "Configurations",
    __name__,
    description="Operations on TFDS configurations",
    url_prefix="/api/configs",
)


def is_served(config_name):
    data = read_config(config_name)
    if data is None:
        return True
    return "noserve" not in data.get("tfds_config", [])

def printlog():
    print("#" * 20, request.method, request.path)


@blp.route("/")
class ConfigList(MethodView):
    @blp.response(200, ConfigListResponseSchema)
    def get(self):
        printlog()
        """List all served configuration files"""
        config_files = [c for c in list_configs() if is_served(c)]
        return {"configs": config_files}


@blp.route("/<string:config_name>")
class ConfigResource(MethodView):
    @blp.response(200, ConfigFileResponseSchema)
    @blp.response(404)
    def get(self, config_name):
        """Retrieve a configuration file"""
        printlog()
        if not is_served(config_name):
            abort(404, message=f"Configuration '{config_name}' not found")
        data = read_config(config_name)
        if data is None:
            abort(404, message=f"Configuration '{config_name}' not found")
        return data, 200

    @blp.arguments(ConfigFileSchema)
    @blp.response(201, ConfigFileResponseSchema)
    def post(self, config_data, config_name):
        """Create or update a configuration file"""
        printlog()
        if not is_served(config_name):
            abort(400, message=f"Permission denied, '{config_name}' is not served through the api.")
        if "noserve" in config_data.get("tfds_config", []):
            abort(
                400,
                message=f"Permission denied, can't save 'noserve' configs thourgh the api, that would be non reversible.",
            )
        write_config_to_file(config_name=config_name, config_data=config_data)
        return read_config(config_name), 201

    @blp.response(204)
    def delete(self, config_name):
        """Delete a configuration file"""
        printlog()
        if not is_served(config_name):
            abort(400, message=f"Permission denied, '{config_name}' is not served through the api.")
        delete_config(config_name)
        return "", 204
