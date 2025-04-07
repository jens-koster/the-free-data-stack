FROM bitnami/spark:3.5.0
WORKDIR /app

# Add Hadoop AWS and AWS SDK JARs for S3 support
#ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.5/hadoop-aws-3.3.5.jar /opt/bitnami/spark/jars/
#ADD https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.524/aws-java-sdk-bundle-1.12.524.jar /opt/bitnami/spark/jars/

# currently we have no dependencies, but I leave this part around in case we do...
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH