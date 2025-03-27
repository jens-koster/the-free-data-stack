import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    os.environ["YAML_DATA_PATH"] = os.path.abspath("./tfds-config/yaml_data")
    os.environ["TFSD_CONFIG_LOCALHOST"] = "Yes please"
    os.environ.pop("TFSD_CONFIG_LOCALHOST", None)
    app.run(debug=True, host="127.0.0.1", port=8005)
