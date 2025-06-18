
# hive catalog
hive catalog is run as a module in spark so requires no separate container.

To get the hive metastore up and running I had to manually install the database from scripts on postgres. Starting on 1.2 and upgrading until I reached my current version.
There's a tool for it, schematool, I should explore that, or create a freeds command to do download and install.

Scripts are located here:
https://github.com/apache/hive/tree/master/standalone-metastore/metastore-server/src/main/sql/postgres
