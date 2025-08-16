# Repository Guidelines

## Project Structure & Module Organization
- Root: `README.md`, CI at `.github/workflows/tests.yml`.
- Tests: `tests/` holds all checks and helpers.
  - Client: `tests/lib/two_captcha_client.py` (2Captcha API wrapper).
  - Env example: `tests/.env.example`. Use `tests/.env` locally.

## Build, Test, and Development Commands
- Install (smoke): `pip install pytest requests python-dotenv`
- Install (E2E): `pip install playwright && python -m playwright install --with-deps chromium`
- Run smoke: `pytest -m smoke -q`
- Run E2E: `pytest -m e2e -q`
- Cloudflare challenge (optional/brittle): `RUN_CF_CHALLENGE_TEST=1 pytest -m cloudflare_challenge -q`
- Single test example: `pytest tests/test_balance.py::test_balance_available -q`

## Coding Style & Naming Conventions
- Language: Python 3.10+.
- Style: PEP 8; 4-space indentation; `snake_case` for functions/variables, `CapWords` for classes.
- Tests: files match `test_*.py`; small, focused assertions; prefer markers `smoke`, `e2e`, `cloudflare_challenge` for scope.
- Networking: call 2Captcha only via `TwoCaptchaClient` for consistency.

## Testing Guidelines
- Framework: `pytest` with fixtures from `tests/conftest.py`.
- Env: set `TWOCAPTCHA_API_KEY` (CI uses a secret). Locally, add it to `tests/.env`:
  ```
  TWOCAPTCHA_API_KEY=your_key_here
  ```
- Skips: tests skip automatically if the key is missing; E2E requires Playwright.
- Determinism: keep smoke tests quick and reliable; reserve flaky/external flows for `e2e` or the challenge marker.

## Commit & Pull Request Guidelines
- Commits: concise, present-tense summary; include scope when helpful. Example: `ci: add smoke and e2e jobs`.
- PRs: describe intent, changes, and how to test; link issues; include logs/screenshots for E2E.
- Checks: run `pytest -m smoke` locally and ensure CI is green before merge.
- Secrets: never commit `tests/.env` or keys.

## Security & Configuration Tips
- GitHub Actions: add `TWOCAPTCHA_API_KEY` under Settings → Secrets and variables → Actions → Secrets.
- E2E in CI: set repo variable `RUN_E2E=1` to enable the job.
- Cloudflare challenge test is experimental; enable only when debugging that flow.

