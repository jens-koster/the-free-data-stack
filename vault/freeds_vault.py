import os
import requests
from pathlib import Path
from typing import Optional

os.environ['FREEDS_VAULT_URI']="http://127.0.0.1:8200"

class BaoPaths:
    def __init__(self):
        self.mount = "config"
        addr = os.environ.get("FREEDS_VAULT_URI")
        if not addr:
            raise RuntimeError("FREEDS_VAULT_URI is not set")
        self.uri = addr.rstrip("/")

        self.v1_path = f"{self.uri}/v1"
        self.init_path = f"{self.v1_path}/sys/init"
        self.sys_mount_path = f"{self.v1_path}/sys/mounts/{self.mount}"
        self.data_path = f"{self.v1_path}/{self.mount}/data"
        self.metadata_path = f"{self.v1_path}/{self.mount}/metadata"
        self.token_path =f"{self.v1_path}/auth/token"

    def plugin_path(self, plugin: str) -> str:
        """Return the full vault path for a plugin's config (no trailing slash)."""
        return f"{self.data_path}/{plugin}"

    def plugin_meta_path(self, plugin: str) -> str:
        """Return the full vault path for a plugin's config (no trailing slash)."""
        return f"{self.metadata_path}/{plugin}"

class BaoClient:

    def __init__(self):
        self.root_token_file = Path.home() / ".freeds/root_token.txt"
        self.root_token: Optional[str] = None
        self.timeout = 5
        self.session = requests.Session()
        self.policy_name = "ro-config"
        self.paths = BaoPaths()

    def header(self):
        """Return headers for vault requests."""
        h = {"Content-Type": "application/json"}
        if self.root_token:
            h["X-Vault-Token"] = self.root_token
        return h

    def read_plugin_config(self, plugin: str = None)->dict:
        """Read plugin config from vault."""
        if not plugin:
            raise ValueError("plugin required")

        result = self.session.get(
            self.paths.plugin_path(plugin),
            headers=self.header(),
            timeout=self.timeout)
        if result.status_code == 404:
            return {}
        return result.json()

    def delete_plugin_config(self, plugin: str)->None:
        """Hard delete plugin config from vault."""
        result = self.session.delete(
            self.paths.plugin_meta_path(plugin),
            headers=self.header(),
            timeout=self.timeout)
        if result.status_code == 404:
            return
        result.raise_for_status()

    def write_plugin_config(self, plugin: str, config:dict)->None:
        """Write plugin config to vault."""
        if plugin is None:
            raise ValueError("plugin required")

        result = self.session.post(
            self.paths.plugin_path(plugin),
            headers=self.header(),
            json={"data": config},
            timeout=self.timeout)
        result.raise_for_status()

    def post_raw(self, path: str, body=None)->dict:
        """POST to vault, return response json or raise."""
        result = self.session.post(path, headers=self.header(), json=body, timeout=self.timeout)
        if result.status_code == 204:
            return {}
        if not result.ok:
            raise RuntimeError(f"POST failed: {result.status_code} {result.text}")
        return result.json()

    def is_initialized(self) -> bool:
        """Check if vault is initialized."""
        r = self.session.get(self.paths.init_path, headers=self.header(), timeout=self.timeout)
        if not r.ok:
            raise RuntimeError(f"is_initialized failed, is vault running?: {r.status_code} {r.text}")
        return bool(r.json().get("initialized"))

    def create_plugin_token(self, plugin: str) -> str:
        """Create a long-lived token for a plugin, store it in vault, return it."""
        if not plugin:
            raise ValueError("plugin required")
        r = self.post_raw(
            f"{self.paths.token_path}/create-orphan",
            {
                "policies": [self.policy_name],
                "ttl": "876000h",
                "explicit_max_ttl": "876000h",
                "display_name": plugin
            }
        )
        token = r["auth"]["client_token"]
        self.write_plugin_config(f"freeds/plugin-tokens/{plugin}", {"token": token})
        return token

    def init(self) -> bool:
        """Initialize vault if not already initialized. Returns bool indicating success."""
        if self.root_token_file.exists():
            with open(self.root_token_file, "r") as f:
                self.root_token = f.read().strip()
            if self.is_initialized():
                return True
        data = self.post_raw(self.paths.init_path, {"secret_shares": 1, "secret_threshold": 1})
        root_token = data["root_token"]
        self.root_token = root_token
        with open(self.root_token_file, "w") as f:
            f.write(root_token)

        # enable the config mount
        try:
            self.post_raw(
                self.paths.sys_mount_path,
                {"type": "kv", "options": {"version": "2"}}
            )
        except RuntimeError as e:
            if "path is already in use" not in str(e):
                raise

        # global read policy for plugin tokens
        # NOTE: HCL uses mount-relative paths, not full URLs.
        hcl = (
            f'path "{self.paths.mount}/data/*"     {{ capabilities = ["read"] }}\n'
            f'path "{self.paths.mount}/metadata/*" {{ capabilities = ["list", "read"] }}\n'
        )
        self.post_raw(f"{self.paths.v1_path}/sys/policies/acl/{self.policy_name}", {"policy": hcl})

        return self.is_initialized()

    def close(self):
        self.session.close()


# --- minimal demo ---
if __name__ == "__main__":
    # export FREEDS_VAULT_URI="http://127.0.0.1:8200"
    client = BaoClient()
    root = client.init()
    if root:
        print("Vault initialized. Root token:", root[:8], "…")
    else:
        print("Vault already initialized.")

    client.write_plugin_config("api", {"URL": "http://svc:8080", "DEBUG": "true"})
    print("api:", client.read_plugin_config("api"))

    tok = client.create_plugin_token("api")
    print("api token:", tok[:10], "…")

    client.delete_plugin_config("api")
    print("api after delete:", client.read_plugin_config("api"))

    client.close()
