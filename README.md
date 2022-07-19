saksa - experiment chat application with python, kafka and stuffs
---

# Configurations

```
SAKSA_ENV
```
Default to `production`, which requires front-end to be built.

Otherwise, use `development` which proxies requests from front-end server.

```
KAFKA_BOOTSTRAP_SERVERS
```
Required if `SAKSA_ENV` is `production`.

Default: `127.0.0.1`, for development only.

```
SAKSA_DEBUG
```
Verbose logs.

# Development

0. Install dependencies

- Python `poetry install`
- Front-end `yarn install`

1. Start front-end

```
$ yarn dev
```

2. Start back-end

```
$ uvicorn --factory saksa:create_app --log-level=debug --reload
```

3. Access to the application on `http://localhost:8000`

# Production build

Not yet
