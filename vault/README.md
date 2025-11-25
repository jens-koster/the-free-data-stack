# Freeds Vault
The OpenBao vault is a central point in freeds.
Freeds is initialized by locating all config templates in the plugins and storing those in the vault.

Then secrets are seeded.

As far as possible the secrets are applied to the plugins, meaning we set passwords according to the vault value.

Each plugin has a "folder" in the vault. With some predefied folders.
* config - name-value from config.yaml
* plugin - the plugin info from plugin.yaml
* meta - meta data, like repo name, folder name
