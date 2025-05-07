
echo "downloading jar packages to package_jars"
rm -rf package_jars
mkdir -p package_jars
coursier fetch \
    io.delta:delta-spark_2.12:3.2.0 \
    org.apache.hadoop:hadoop-aws:3.3.4 \
    org.apache.hadoop:hadoop-common:3.3.4 \
    com.amazonaws:aws-java-sdk-bundle:1.12.262 \
    org.postgresql:postgresql:42.6.0 \
    org.apache.hive:hive-metastore:2.3.9 \
    org.datanucleus:datanucleus-core:4.1.17 \
    org.datanucleus:datanucleus-api-jdo:4.2.4 \
    org.datanucleus:datanucleus-rdbms:4.1.19 \
    javax.jdo:jdo-api:3.0.1 \
    com.google.guava:guava:30.1.1-jre \
    --exclude org.pentaho:pentaho-aggdesigner-algorithm \
    --exclude log4j:log4j \
    --classpath | tr ':' '\n' | while read jar; do cp "$jar" package_jars/; done


rm -rf docker_jars
echo "copying spark jars from apache image"
docker create --name spark-temp apache/spark:3.5.5
docker cp spark-temp:/opt/spark/jars ./docker_jars
docker rm spark-temp

echo "ensuring:"
echo "no log4j from packages is used"
rm ./package_jars/log4j*

rm /Users/jens/src/the-free-data-stack/.venv/lib/python3.8/site-packages/pyspark/jars/log4j-1.2-api-2.20.0.jar
rm ./jars/log4j-1.2-api-2.20.0.jar

echo "no datanucleus from docker is used"
rm ./docker_jars/datanucleus*
echo "guava from packages i sused"
rm ./docker_jars/guava*

python3 fix_jars.py
rm -rf jars
mkdir jars

cp docker_jars/*.jar jars/
cp package_jars/*.jar jars/

echo "jars done!"
