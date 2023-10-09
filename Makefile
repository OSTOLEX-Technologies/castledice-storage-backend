# these will speed up builds, for docker-compose >= 1.25
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

build:
	docker-compose build

up:
	docker-compose up -d

up-dev:
	docker-compose --profile dev up -d

up-test:
	docker-compose --profile test up -d

down:
	docker-compose down --remove-orphans

integration-tests: up-test
	docker-compose run --rm --no-deps app-test --command="python db.py && pytest /tests/integration"

e2e-tests: up-test
	docker-compose run --rm --no-deps --entrypoint=python db.py && pytest app /tests/e2e

e2e-tests-sqlite:
	DATABASE_TYPE=sqlite pytest tests/e2e

test-sqlite:
	DATABASE_TYPE=sqlite pytest -s

db:
	docker-compose up -d db

test-db:
	docker-compose up -d test-db