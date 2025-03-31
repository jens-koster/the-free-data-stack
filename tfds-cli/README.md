# tfds cli
Python scripts/modules to interact with and control the tfds.

# dependencies
## tfds
needs setup.sh to be run.
## nb deploy
tfds
tfds-config (for the s3 config)
s3-ninja

# todo
At some point this must be made an installable cli, allowing git hooks in pipe-dreams to execute deploynb.py
Meaning deploynb should use a local config file for notebook folders in the deployed repo and tfds-config for the s3 config.

Defaulting to folder names ".", and "./temp" meaning we'd need no config file for default usage: look for all notebooks in repo folder. Use a ./temp as tempfolder, create and remove it if it's not pre-existing.

pipe-dreams would add temp/ to gitignore.

nbdeploy needs to ignore the tempfolder.

tfds-config storage module should be moved here as well, providing unified config file access from python for:
* CRUD
* set_env

tfds-config should be synlinked to /tmp/tfds/config
