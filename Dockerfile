FROM node:lts-alpine AS assests-builder

WORKDIR /app

COPY ./package.json ./
COPY ./yarn.lock ./
COPY ./vite.config.js ./

RUN mkdir saksa && yarn install

COPY ./index.html ./
COPY ./frontend ./frontend
COPY ./templates ./templates

RUN ls -alt

RUN yarn build

FROM docker.io/python:3.8 AS saksa-builder

ENV PATH="/root/.poetry/bin:$PATH"
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

WORKDIR /app

COPY ./pyproject.toml ./
COPY ./poetry.lock ./
COPY ./saksa ./saksa
COPY --from=assests-builder /app/saksa/static ./saksa/static

RUN poetry build

FROM python:3.8

COPY --from=saksa-builder /app/dist/saksa-0.1.0-py3-none-any.whl /
COPY ./vendors/rocksdb-6.29.5 /rocksdb

RUN apt update && apt install libsnappy-dev liblz4-dev -y && rm -rf /var/lib/apt/lists/*

RUN CPLUS_INCLUDE_PATH=${CPLUS_INCLUDE_PATH}:/rocksdb/include \
	LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/rocksdb/lib \
	LIBRARY_PATH=${LIBRARY_PATH}:/rocksdb/lib \
	pip install saksa-0.1.0-py3-none-any.whl

RUN useradd saksa

USER saksa
