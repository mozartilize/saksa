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

FROM docker.io/python:3.10 AS saksa-builder

ARG VERSION=$VERSION

ENV PATH="/root/.local/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR /app

COPY ./pyproject.toml ./
COPY ./poetry.lock ./
COPY ./saksa ./saksa
COPY --from=assests-builder /app/saksa/static ./saksa/static

RUN poetry build

RUN python -m venv /.venv

ENV PATH="/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/.venv"

RUN pip install dist/saksa-${VERSION}-py3-none-any.whl

FROM python:3.10-slim

ARG VERSION=$VERSION

RUN apt update && apt install libsnappy1v5 librdkafka1 -y && rm -rf /var/lib/apt/lists/*

COPY --from=saksa-builder /app/dist/saksa-${VERSION}-py3-none-any.whl /saksa-${VERSION}-py3-none-any.whl

COPY --from=saksa-builder /.venv /.venv
ENV PATH="/.venv/bin:$PATH"
ENV VIRTUAL_ENV="./venv"

RUN useradd -m saksa

USER saksa

WORKDIR /home/saksa
