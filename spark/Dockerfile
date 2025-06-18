FROM apache/spark:3.5.5

ENV SPARK_MODE=master \
    SPARK_MASTER_WEBUI_PORT=8010 \
    SPARK_WORKER_WEBUI_PORT=8011


# doing things in /opt requires root access
USER root

# Upgrade from the ancient 3.8 that comes with the spark image:
# install Python 3.11 and tools
RUN apt-get update && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install requirements with Python 3.11
COPY requirements.txt requirements.txt
RUN python3.11 -m ensurepip --upgrade \
    && python3.11 -m pip install --upgrade pip setuptools wheel
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt

EXPOSE 7077 8010 8011 8012
# for some reason papermill build needs the saprk home folder...
RUN mkdir -p /opt/spark/jars /opt/spark/conf /opt/freeds/data /opt/freeds/spark/jars /home/spark
RUN chown -R spark:spark /home/spark

ENV SPARK_CLASSPATH="/opt/freeds/spark/jars/*"

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY package_jars/*.jar /opt/freeds/spark/jars/
# COPY jars/*.jar /opt/freeds/spark/jars/

# Clean out stuff we want to upgrade
RUN find /opt/spark/jars/ -name "guava-*.jar" -delete
RUN find /opt/spark/jars/ -name "datanucleus*.jar" -delete

# for spark master/workers to find it
# COPY ./conf/ /opt/spark/conf/

# we're using this conf folder in local development,
# let's make it the same in master, worker and driver dockers.
COPY ./conf/ /opt/freeds/spark/conf/
ENV SPARK_CONF_DIR=/opt/freeds/spark/conf

VOLUME /opt/freeds/data

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

USER spark

# override the spark entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
