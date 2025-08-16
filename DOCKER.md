# Docker & Compose

This repository includes a Docker setup to run tests in an isolated environment. It provides a small image for smoke tests and a heavier Playwright image for E2E.

## Prerequisites
- Docker and Docker Compose (v2)
- A `.env` file at the repo root with your key:
  
  `TWOCAPTCHA_API_KEY=your_key_here`

## Build images
- Smoke (fast): `docker compose build tests`
- E2E (heavy): `docker compose build e2e`

## Start an interactive shell
- Smoke: `docker compose run --rm tests`
  - Drops you into `/app` inside the container (the repo is mounted).
  - The container environment loads variables from your root `.env`.
- E2E: `docker compose run --rm e2e`

Alternatively, to keep a long-running container:
- `docker compose up -d tests` then `docker compose exec tests bash`
- For E2E: `docker compose up -d e2e` then `docker compose exec e2e bash`

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
  - `docker compose run --rm e2e bash -lc "pytest -m e2e -q"`
- Challenge:
  - `docker compose run --rm -e RUN_CF_CHALLENGE_TEST=1 e2e bash -lc "pytest -m cloudflare_challenge -q"`
- All tests:
  - `docker compose run --rm tests bash -lc "pytest -q"`

## Notes
- Smoke uses `python:3.12-slim` for quick pulls/builds.
- E2E uses Playwright’s Python base and installs Chromium; the first pull can be large/slow.
- Local files `tests/.env` and root `.env` are ignored by Git; do not commit secrets.
- If you prefer not to mount the repo, copy files in a custom Dockerfile stage instead.
