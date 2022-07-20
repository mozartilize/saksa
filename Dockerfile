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

RUN apt update && apt install cmake libsnappy-dev liblz4-dev -y && rm -rf /var/lib/apt/lists/*

ENV MAX_PROCS=8
ENV [[ $(nproc) -lt MAX_PROCS ]] && MAX_PROCS=$(nproc)

RUN curl -L https://codeload.github.com/facebook/rocksdb/tar.gz/refs/tags/v6.29.5 -o rocksdb.tar.gz && \
	tar -xf rocksdb.tar.gz && \
	mv rocksdb-6.29.5 rocksdb && \
	cd rocksdb && \
	mkdir build && cd build && \
	cmake -DCMAKE_BUILD_TYPE=Release -DWITH_SNAPPY=1 -DWITH_LZ4=1 -DWITH_GFLAGS=0 .. && \
	make -j$MAX_PROCS

ENV PATH="/root/.poetry/bin:$PATH"
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

WORKDIR /app

COPY ./pyproject.toml ./
COPY ./poetry.lock ./
COPY ./saksa ./saksa
COPY --from=assests-builder /app/saksa/static ./saksa/static

RUN poetry build

RUN python -m venv .venv

ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"

RUN CPLUS_INCLUDE_PATH=${CPLUS_INCLUDE_PATH}:/rocksdb/include \
	LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/rocksdb/build \
	LIBRARY_PATH=${LIBRARY_PATH}:/rocksdb/build \
	pip install dist/saksa-0.1.0-py3-none-any.whl

FROM python:3.8-slim

RUN apt update && apt install libsnappy1v5 -y && rm -rf /var/lib/apt/lists/*

COPY --from=saksa-builder /rocksdb/build/librocksdb.so.6.29.5 /usr/lib/x86_64-linux-gnu/librocksdb.so.6

COPY --from=saksa-builder /app/.venv /.venv
ENV PATH="/.venv/bin:$PATH"
ENV VIRTUAL_ENV="./venv"

RUN useradd saksa

USER saksa
