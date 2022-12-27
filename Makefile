SHELL = bash

PROJ := $(shell basename `pwd`)
DOCKEREXCUTABLE = $(shell type podman >/dev/null 2>&1 && echo "podman" || echo "docker")
VERSION := $(shell grep ^version pyproject.toml | sed 's/version = //' | xargs | sed 's/^v//')
GIT_REF := $(shell [ -d ".git" ] && git rev-parse --short HEAD || echo '')
BEFORE_REF := HEAD~1
REF := HEAD
ifeq ($(GIT_REF), '')
BUILD_VERSION := ${VERSION}
else
BUILD_VERSION := ${VERSION}+${GIT_REF}
endif

foo: .git
	@echo 'hello world'
	@echo ${PROJ}

check:
	-poetry run flake8 $(shell git --no-pager diff ${BEFORE_REF}..${REF} --name-only --diff-filter=ACMR | grep .py)
	-poetry run pyright $(shell git --no-pager diff ${BEFORE_REF}..${REF} --name-only --diff-filter=ACMR | grep .py)
	-yarn run eslint $(shell git --no-pager diff ${BEFORE_REF}..${REF} --name-only --diff-filter=ACMR | grep -E '.jsx?')

test:
	pytest tests

build:
	yarn build
	poetry version v${BUILD_VERSION}
	poetry build
	poetry version v${VERSION}

build-docker:
	$(DOCKEREXCUTABLE) build --build-arg VERSION=v${BUILD_VERSION} -t saksa:v${VERSION}.${GIT_REF} -t saksa:latest -f docker/Dockerfile .
