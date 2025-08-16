SERVICE ?= tests

.PHONY: build shell up exec down logs test-smoke test-e2e test-challenge

build:
	docker compose build

shell:
	docker compose run --rm $(SERVICE)

up:
	docker compose up -d

exec:
	docker compose exec $(SERVICE) bash

down:
	docker compose down -v

logs:
	docker compose logs -f $(SERVICE)

test-smoke:
	docker compose run --rm $(SERVICE) bash -lc "pytest -m smoke -q"

test-e2e:
	docker compose run --rm $(SERVICE) bash -lc "pytest -m e2e -q"

test-challenge:
	docker compose run --rm -e RUN_CF_CHALLENGE_TEST=1 $(SERVICE) bash -lc "pytest -m cloudflare_challenge -q"

