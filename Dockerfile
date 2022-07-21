ARG VERSION

FROM node:lts-alpine AS assests-builder

WORKDIR /app

COPY ./package.json ./
COPY ./yarn.lock ./
COPY ./vite.config.js ./

RUN mkdir saksa && yarn install

COPY ./index.html ./
COPY ./frontend ./frontend
COPY ./templates ./templates

RUN yarn build

FROM docker.io/python:3.8 AS saksa-builder

ARG VERSION=$VERSION

ENV PATH="/root/.poetry/bin:$PATH"
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

RUN apt update && apt install libsnappy-dev liblz4-dev -y && rm -rf /var/lib/apt/lists/*
COPY ./vendors/rocksdb /rocksdb

WORKDIR /app

COPY ./pyproject.toml ./
COPY ./poetry.lock ./
COPY ./saksa ./saksa
COPY --from=assests-builder /app/saksa/static ./saksa/static

RUN poetry build

RUN python -m venv /.venv

ENV PATH="/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/.venv"

RUN CPLUS_INCLUDE_PATH=${CPLUS_INCLUDE_PATH}:/rocksdb/include \
	LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/rocksdb/lib \
	LIBRARY_PATH=${LIBRARY_PATH}:/rocksdb/lib \
	pip install dist/saksa-${VERSION}-py3-none-any.whl

FROM python:3.8-slim

ARG VERSION=$VERSION

RUN apt update && apt install libsnappy1v5 -y && rm -rf /var/lib/apt/lists/*

COPY ./vendors/rocksdb/lib/librocksdb.so /usr/lib/x86_64-linux-gnu/librocksdb.so.6
COPY --from=saksa-builder /app/dist/saksa-${VERSION}-py3-none-any.whl /saksa-${VERSION}-py3-none-any.whl

COPY --from=saksa-builder /.venv /.venv
ENV PATH="/.venv/bin:$PATH"
ENV VIRTUAL_ENV="./venv"

RUN useradd -m saksa

USER saksa

WORKDIR /home/saksa
