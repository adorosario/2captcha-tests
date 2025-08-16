# Docker & Compose

This repository includes a Docker setup to run tests in an isolated environment with optional Playwright E2E support.

## Prerequisites
- Docker and Docker Compose (v2)
- A `.env` file at the repo root with your key:
  
  `TWOCAPTCHA_API_KEY=your_key_here`

## Build the image
- `docker compose build`

## Start an interactive shell
- `docker compose run --rm tests`
  - This drops you into `/app` inside the container (the repo is mounted).
  - The container environment loads variables from your root `.env`.

Alternatively, to keep a long-running container:
- `docker compose up -d` then `docker compose exec tests bash`

## Run tests (inside container)
- Smoke (no browser): `pytest -m smoke -q`
- E2E (Playwright): `pytest -m e2e -q`
- Cloudflare challenge (optional/brittle):
  - `export RUN_CF_CHALLENGE_TEST=1`
  - `pytest -m cloudflare_challenge -q`

## Quick one-liners (no interactive shell)
- Smoke:
  - `docker compose run --rm tests bash -lc "pytest -m smoke -q"`
- E2E:
  - `docker compose run --rm tests bash -lc "pytest -m e2e -q"`
- Challenge:
  - `docker compose run --rm -e RUN_CF_CHALLENGE_TEST=1 tests bash -lc "pytest -m cloudflare_challenge -q"`
- All tests:
  - `docker compose run --rm tests bash -lc "pytest -q"`

## Notes
- The image is based on Playwright’s Python base, so E2E tests work without extra system deps.
- Local files `tests/.env` and root `.env` are both ignored by Git; do not commit secrets.
- If you prefer not to mount the repo, copy files in a custom Dockerfile stage instead.
