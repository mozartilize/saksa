SHELL = bash

PROJ := $(shell basename `pwd`)
DOCKEREXCUTABLE = $(shell type podman >/dev/null 2>&1 && echo "podman" || echo "docker")
VERSION := $(shell grep ^version pyproject.toml | sed 's/version = //' | xargs | sed 's/^v//')
GIT_REF := $(shell [ -d ".git" ] && git rev-parse --short HEAD || echo '')
GIT_BASE_REF := HEAD~1
ifeq ($(GIT_REF), '')
BUILD_VERSION := ${VERSION}
else
BUILD_VERSION := ${VERSION}+${GIT_REF}
endif
CHANGED_FILES=git --no-pager diff ${GIT_BASE_REF}..${GIT_REF} --name-only --diff-filter=ACMR

foo: .git
	@echo 'hello world'
	@echo ${PROJ}

check:
	poetry run flake8 $(shell $(CHANGED_FILES) | grep .py)
	poetry run pyright $(shell $(CHANGED_FILES) | grep .py)
	poetry run isort -c $(shell $(CHANGED_FILES) | grep .py)
	yarn run eslint $(shell $(CHANGED_FILES) | grep -E .jsx?$)

test:
	pytest tests

build:
	yarn build
	poetry version v${BUILD_VERSION}
	poetry build
	poetry version v${VERSION}

build-docker:
	$(DOCKEREXCUTABLE) build --build-arg VERSION=v${BUILD_VERSION} -t saksa:v${VERSION}.${GIT_REF} -t saksa:latest -f docker/Dockerfile .
