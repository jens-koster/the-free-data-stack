#!/bin/bash
set -e

export SPARK_DIST_CLASSPATH="$SPARK_CLASSPATH"
export SPARK_CONF_DIR=/opt/spark/conf

# Expand environment variables in spark-defaults.conf.template
if [ -f /opt/spark/conf/spark-defaults.conf.template ]; then
  envsubst < /opt/spark/conf/spark-defaults.conf.template > /opt/spark/conf/spark-defaults.conf
fi

ls /opt/spark/sbin
if [ "$SPARK_MODE" = "master" ]; then
  echo "Starting Spark Master...x"
  /opt/spark/sbin/start-master.sh --host "$SPARK_MASTER_HOST" --webui-port "$SPARK_MASTER_WEBUI_PORT"
elif [ "$SPARK_MODE" = "worker" ]; then
  echo "Starting Spark Worker...x"
  /opt/spark/sbin/start-worker.sh "$SPARK_MASTER_URL" --webui-port "$SPARK_WORKER_WEBUI_PORT"
else
  echo "SPARK_MODE must be 'master' or 'worker'"
  exit 1
fi

tail -f /dev/null
