help:
	@echo "help                               -- prints this help"
	@echo "build                              -- builds Docker containers"
	@echo "run                                -- start the average face calculus"
	@echo "test                               -- start test suite"
	@echo "psql                               -- psql terminal to postgres db"
	@echo "bash                               -- terminal to app service"
	@echo "version                            -- print out the app version"
	@echo "clean                              -- remove pyc and pycaches files"

GREEN="\\e[32m"
BLUE="\\e[94m"
REGULAR="\\e[39m"
RED="\\e[91m"

dkc:=docker-compose

up:
	@$(dkc) up --build -d
	@# prestart.sh not being called by tiangolo img ._.
	@$(dkc) exec app /bin/sh -c /app/prestart.sh
	@$(dkc) logs -f

down:
	@$(dkc) down

stop:
	@$(dkc) stop

build:
	@$(dkc) build

test:
	@$(dkc) run app pytest tests

psql:
	@# TODO: use env vars here
	@$(dkc) exec db psql --username=postgres --dbname=app

bash:
	@$(dkc) run app bash

version:
	@cat app/__init__.py

clean:
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

.PHONY: help build run test up down stop psql bash version clean
