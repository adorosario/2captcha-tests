# Repository Guidelines

## Project Structure & Module Organization
- Root: `README.md`; CI at `.github/workflows/tests.yml`.
- Tests live in `tests/`.
  - 2Captcha wrapper: `tests/lib/two_captcha_client.py` (use this for all API calls).
  - Fixtures and markers: `tests/conftest.py`.
  - Env example: `tests/.env.example` (copy to `tests/.env` locally).
- This repo is a lightweight test harness; keep additions minimal and focused.

## Build, Test, and Development Commands
- Install (smoke): `pip install pytest requests python-dotenv`.
- Install (E2E): `pip install playwright && python -m playwright install --with-deps chromium`.
- Run smoke: `pytest -m smoke -q` (fast, deterministic checks).
- Run E2E: `pytest -m e2e -q` (requires Playwright; may hit network).
- Optional Cloudflare: `RUN_CF_CHALLENGE_TEST=1 pytest -m cloudflare_challenge -q` (brittle; for debugging only).
- Single test: `pytest tests/test_balance.py::test_balance_available -q`.

## Coding Style & Naming Conventions
- Python 3.10+; PEP 8; 4‑space indentation.
- Names: `snake_case` for functions/variables; `CapWords` for classes.
- Tests: files named `test_*.py`; small, focused assertions; prefer markers `smoke`, `e2e`, `cloudflare_challenge` to scope runs.
- Networking: call 2Captcha only via `TwoCaptchaClient` in `tests/lib/two_captcha_client.py`.

## Testing Guidelines
- Framework: `pytest`; shared fixtures in `tests/conftest.py`.
- Env: set `TWOCAPTCHA_API_KEY`. Locally, add it to `tests/.env`:
  
  ```
  TWOCAPTCHA_API_KEY=your_key_here
  ```
  
- Tests skip automatically if the key is missing.
- Determinism: keep smoke tests quick and reliable; reserve flaky/external flows for `e2e` or the Cloudflare marker.

## Commit & Pull Request Guidelines
- Commits: concise, present‑tense summaries; include scope when helpful. Example: `ci: add smoke and e2e jobs`.
- PRs: explain intent, changes, and how to test; link issues; include logs/screenshots for E2E runs.
- Checks: run `pytest -m smoke -q` locally and ensure CI passes before merging.
- Secrets: never commit `tests/.env` or keys.

## Security & Configuration Tips
- GitHub Actions: add `TWOCAPTCHA_API_KEY` under Settings → Secrets and variables → Actions → Secrets.
- To enable E2E in CI, set repo variable `RUN_E2E=1`.
- The Cloudflare challenge test is experimental; enable only when actively debugging that flow.

