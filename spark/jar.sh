
echo "downloading jar packages to package_jars"
rm -rf package_jars
mkdir -p package_jars
# org.apache.iceberg:iceberg-common:1.9.2 \
# org.apache.iceberg:iceberg-api:1.9.2 \
# org.apache.iceberg:iceberg-core:1.9.2 \


coursier fetch \
    org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.9.2 \
    org.apache.hadoop:hadoop-aws:3.3.4 \
    org.apache.hadoop:hadoop-common:3.3.4 \
    com.amazonaws:aws-java-sdk-bundle:1.12.262 \
    org.postgresql:postgresql:42.7.3 \
    --exclude org.pentaho:pentaho-aggdesigner-algorithm \
    --exclude log4j:log4j \
    --exclude org.apache.parquet:parquet-hadoop-bundle \
    | tr ':' '\n' | while read jar; do cp "$jar" package_jars/; done

rm -rf docker_jars
echo "copying spark jars from apache image"
docker create --name spark-temp apache/spark:3.5.5
docker cp spark-temp:/opt/spark/jars ./docker_jars
docker rm spark-temp

echo "ensuring:"

echo "only docker log4j is used"
rm ./package_jars/log4j*
rm ./package_jars/logback*
rm ./package_jars/slf4j*
rm ~/src/the-free-data-stack/.venv/lib/python3.8/site-packages/pyspark/jars/log4j-1.2-api-2.20.0.jar
rm ./jars/log4j-1.2-api-2.20.0.jar

echo "legacy jar not used: parquet-hadoop-bundle-1.8.1.jar"
rm ./package_jars/parquet-hadoop-bundle-1.8.1.jar


echo "remove some conflicting jars we got in the package dependecies"
rm ./package_jars/javax.servlet*.jar
rm ./package_jars/servlet-api-*.jar
rm ./package_jars/jetty-*.jar
rm ./package_jars/netty-*.jar

python3 fix_jars.py

echo "jars done!"
