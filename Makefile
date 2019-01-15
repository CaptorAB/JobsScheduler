include .env
export
GIT_HASH := $(shell git rev-parse --short HEAD)
DATE :=  $(shell date +%Y_%m_%d_%H)

venv: requirements.txt
	virtualenv -p python3 --setuptools venv
	venv/bin/pip install --upgrade -r requirements.txt

test:
	PYTHONPATH=${PWD} venv/bin/nosetests -vv --nologcapture --nocapture ./

.PHONY: test


start:
	PYTHONPATH=${PWD} venv/bin/python3 app/main.py

docker_build:
        docker build -f Dockerfile --tag $(docker_tag):$(DATE)_$(GIT_HASH) .
        docker push ${docker_tag}:$(DATE)_$(GIT_HASH)

