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

    @app.route("/health")
    def health_check():
        return {"status": "healthy"}, 200

    return app
