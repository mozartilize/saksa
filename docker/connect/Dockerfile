FROM debezium/connect:latest

RUN curl -L https://github.com/scylladb/scylla-cdc-source-connector/releases/download/scylla-cdc-source-connector-1.0.1/ScyllaDB-scylla-cdc-source-connector-1.0.1.zip -o /tmp/scylla-kafka-connector-1.0.1.zip && \
    unzip /tmp/scylla-kafka-connector-1.0.1.zip -d $KAFKA_CONNECT_PLUGINS_DIR && \
    rm /tmp/scylla-kafka-connector-1.0.1.zip
