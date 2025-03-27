import ipaddress
import os

import requests
from app.api.schemas.request_models import ConfigFileSchema, ConfigItemSchema
from app.api.schemas.response_models import (ConfigFileResponseSchema,
                                             ConfigItemResponseSchema,
                                             ConfigListResponseSchema)
from app.data.store import list_configs, read_yaml, write_yaml
from bs4 import BeautifulSoup
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint(
    "Configurations",
    __name__,
    description="Operations on TFDS configurations",
    url_prefix="/api/configs",
)


@blp.route("/")
class ConfigList(MethodView):
    @blp.response(200, ConfigListResponseSchema)
    def get(self):
        """List all available configuration files"""
        config_files = list_configs()
        return {"configs": config_files}


def scrape_keys(url):
    """
    Scrapes the given URL to extract 'Access Key' and 'Secret Key' fields.

    Args:
        url (str): The URL of the website to scrape.

    Returns:
        dict: A dictionary containing the extracted keys.
    """

    try:
        # Send a GET request to the website
        print(f"scraping {url}")
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP errors

        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract the keys
        access_key = None
        secret_key = None

        # Find all <dl> elements
        dl_elements = soup.find_all("dl")

        for dl in dl_elements:
            dt = dl.find("dt")
            dd = dl.find("dd")
            if dt and dd:
                label = dt.text.strip()
                value = dd.text.strip()
                if label == "Access Key":
                    access_key = value
                elif label == "Secret Key":
                    secret_key = value

        # Return the extracted keys
        return {"access_key": access_key, "secret_key": secret_key}

    except requests.exceptions.RequestException as e:
        return None


def get_s3():
    """
    Get and set the S3 config by scrapeíng the keys.

    Returns:
        dict: A dictionary containing the S3 configuration.
    """
    if os.environ.get("TFSD_CONFIG_LOCALHOST") or request.args.get("localhost"):
        url = "http://127.0.0.1:8004"
    else:
        url = "http://s3-ninja:9000"

    url_ui = url + "/ui"
    url_s3 = url + "/s3"
    cfg = scrape_keys(f"{url_ui}")
    print(f"scraped {url_ui}: {cfg}")
    data = None
    if cfg is None:
        print("no s3-ninja server found, trying to read s3.yaml")
        data = read_yaml("s3.yaml")
        print(f"found s3.yaml: {data}")
    else:
        print("config found, formatting response from scraped data")
        data = {
            "items": [
                {
                    "name": "url",
                    "value": f"{url}",
                    "description": "URL of the S3 server",
                },
                {
                    "name": "access_key",
                    "value": cfg["access_key"],
                    "description": "Access key of the S3 server",
                },
                {
                    "name": "secret_key",
                    "value": cfg["secret_key"],
                    "description": "Secret key of the S3 server",
                },
            ]
        }
    return data


@blp.route("/s3")
class S3ConfigResource(MethodView):
    @blp.response(200, ConfigFileResponseSchema)
    @blp.response(404)
    def get(self):
        data = get_s3()
        if not data:
            abort(404, message=f"Configuration s3 not found. Is s3-ninja started?")

        return {"name": "s3", "items": data.get("items", [])}


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

        return {
            "name": config_name.replace(".yaml", ""),
            "items": data.get("items", {}),
        }

    @blp.arguments(ConfigFileSchema)
    @blp.response(201, ConfigFileResponseSchema)
    def post(self, config_data, config_name):
        """Create or update a configuration file"""
        # Ensure .yaml extension
        if not config_name.endswith(".yaml"):
            config_name += ".yaml"

        write_yaml(config_name, {"items": config_data["items"]})
        return {
            "name": config_name.replace(".yaml", ""),
            "items": config_data["items"],
        }, 201

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
