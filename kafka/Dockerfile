FROM confluentinc/cp-kafka-connect:8.1.0

WORKDIR /usr/share/java

# confluent-hub comand comes with the official kafka connect image
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-jdbc:10.7.4

# get jdbc driver for Postgres from official site
RUN curl -fSL https://jdbc.postgresql.org/download/postgresql-42.6.0.jar -o postgresql-42.6.0.jar

# install our config to kafka_db inourn postgres server
COPY kafka-connect-config/ /etc/kafka-connect/connectors/

# Expose the Kafka Connect REST API port
EXPOSE 8083