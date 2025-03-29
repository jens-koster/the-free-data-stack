import ipaddress
import os

import requests
from app.api.schemas.request_models import ConfigFileSchema
from app.api.schemas.response_models import (ConfigFileResponseSchema,
                                             ConfigListResponseSchema)
from app.data.store import list_configs, format_response, write_config, read_config, delete_config
from bs4 import BeautifulSoup
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from app.data.store import DATA_PATH

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
    Scrapes the s3-ninja ui and extracts 'Access Key' and 'Secret Key'.
    Args:
        url (str): The URL of the s3-ninja ui.
    Returns:
        dict: A dictionary containing the extracted keys.
    """

    try:
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

        return {"access_key": access_key, "secret_key": secret_key}
    except requests.exceptions.RequestException as e:
        return None


def get_s3():
    """
    Get and set the S3 config by scraping the keys.
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
    data = {}
    if cfg is None:
        print("no s3-ninja server found, trying to read s3.yaml")
        data = read_config("s3")
        print(f"found s3.yaml: {data}")
    else:
        print("config found, formatting response from scraped data")
        data = format_response(
            path=url_ui,
            name='s3',
            notes='scraped from service, did not look for a file',
            config = {
                "url": url_s3,
                "access_key": cfg["access_key"],
                "secret_key": cfg["secret_key"],
            }
        )
    return data

@blp.route("/s3")
class S3ConfigResource(MethodView):
    @blp.response(200, ConfigFileResponseSchema)
    @blp.response(404)
    def get(self):
        data = get_s3()
        if not data:
            abort(404, message=f"Configuration s3 not found. Is s3-ninja started?")
        return data

@blp.route("/<string:config_name>")
class ConfigResource(MethodView):
    @blp.response(200, ConfigFileResponseSchema)
    @blp.response(404)
    def get(self, config_name):
        data = read_config(config_name)
        if not data:
            abort(404, message=f"Configuration '{config_name}' not found")
        return data

    @blp.arguments(ConfigFileSchema)
    @blp.response(201, ConfigFileResponseSchema)
    def post(self, config_data, config_name):
        """Create or update a configuration file"""
        write_config(config_name, config_data)
        return read_config(config_name), 201

    @blp.response(204)
    def delete(self, config_name):
        """Delete a configuration file"""
        delete_config(config_name)
        return "", 204
