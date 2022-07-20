saksa - experiment chat application with python, kafka and stuffs
---

# Requirements

- `python>=3.8`, `poetry`
- `Node>=14`, `yarn`
- `kafka`
- `kafka-connect`
- `scylladb`
- `rocksdb~=6`'s shared library and development files

# Configurations

```
SAKSA_ENV
```
Default to `production`, which requires front-end to be built.

Otherwise, use `development` which proxies requests from front-end server.

```
KAFKA_BOOTSTRAP_SERVERS
```
Required.

Comma separated `host[:port]` of kafka nodes.

Default: `127.0.0.1`, for development only.

```
SCYLLADB_SERVER
```
Required.

The only one address of a node of scylla in cluster.

Default port should be `9042` because it's not configurable yet.

```
SAKSA_DEBUG
```
Verbose logs.

# Development

0. Install dependencies

- Python `poetry install`
- Front-end `yarn install`

For details, you could check the `Dockerfile`.

1. Start services (kafka, scylla, kafka-connect)

You can run with provided `docker-compose.yml`.

```
$ docker-compose up -d
```

For scylladb, you need to manually create `saksa` keyspace.
Then run migrations, with example command:

```
$ cat migrations/00001_create_messages_table/up.cql | docker exec -i saksa_scylladb_1 cqlsh -k saksa
```

The scylla connector requires `messages` table to be created first.

Install the connector:

```
$ curl -XPUT localhost:8083/connectors/ScyllaConnector/config -d @docker/connect/scylla-connector.json -H 'Content-Type: application/json'
```

2. Configuration

Create an `.env` file in the root repo and add values for each setting described above.

3. Start front-end

```
$ yarn dev
```

4. Start back-end

```
$ uvicorn --factory saksa:create_app --log-level=debug --reload
```

5. Start faust worker

```
$ faust -A saksa.kafka_worker worker -l info --without-web
```

6. Access to the application on `http://localhost:8000`

# Production build

1. Build front-end

```
$ yarn build
```

2. Build python package

```
$ poetry build
```

The artifacts are located at `/dist` directory.
