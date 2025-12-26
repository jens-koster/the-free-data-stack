from typing import Any
from flask import jsonify
from app.api.schemas.response_models import (
    ConfigFileResponseSchema,
    ConfigListResponseSchema,
)
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from freeds.config.file import (
    get_config,
    get_current_config_set,
)

blp = Blueprint(
    "Configurations",
    __name__,
    description="Operations on FREEDS configurations",
    url_prefix="/api/configs",
)


def printlog() -> None:
    print("#" * 20, request.method, request.path)


@blp.route("/")
class ConfigList(MethodView):  # type: ignore[misc]
    @blp.response(200, ConfigListResponseSchema)  # type: ignore[misc]
    def get(self) -> list[str]:
        printlog()
        print(get_current_config_set().config_set)
        """List all served configuration files"""
        ls = []
        for key in get_current_config_set().config_set.keys():
            print(key)
            ls.append(str(key))
        return jsonify(ls)


@blp.route("/<string:config_name>")
class ConfigResource(MethodView):  # type: ignore[misc]
    @blp.response(200, ConfigFileResponseSchema)  # type: ignore[misc]
    @blp.response(404)  # type: ignore[misc]
    def get(self, config_name: str) -> tuple[dict[str, Any], int]:
        """Retrieve a configuration file"""
        printlog()
        cfg = get_config(config_name)
        if cfg is None:
            abort(404, message=f"Configuration '{config_name}' not found")
        return cfg.data, 200
