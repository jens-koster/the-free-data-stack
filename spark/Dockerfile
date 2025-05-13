FROM apache/spark:3.5.5

ENV SPARK_MODE=master \
    SPARK_MASTER_WEBUI_PORT=8010 \
    SPARK_WORKER_WEBUI_PORT=8011


# doing things in /opt requires root access
USER root

EXPOSE 7077 8010 8011 8012
# for some reason papermill build needs the saprk home folder...
RUN mkdir -p /opt/spark/jars /opt/spark/conf /opt/tfds/data /opt/tfds/spark/jars /home/spark
RUN chown -R spark:spark /home/spark

ENV SPARK_CLASSPATH="/opt/tfds/spark/jars/*"
COPY package_jars/*.jar /opt/tfds/spark/jars/
# COPY jars/*.jar /opt/tfds/spark/jars/

# Clean out stuff we want to upgrade
RUN find /opt/spark/jars/ -name "guava-*.jar" -delete
RUN find /opt/spark/jars/ -name "datanucleus*.jar" -delete

COPY ./conf/ /opt/spark/conf/

VOLUME /opt/tfds/data

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh


USER spark

# Custom entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
