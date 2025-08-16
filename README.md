# 2Captcha Integration Test Suite

This test suite verifies that your scraper correctly *uses* the 2Captcha API and that your 2Captcha account & credits are working.

## What it covers
- ✅ API connectivity & balance
- ✅ Solve **reCAPTCHA v2** on 2Captcha's official demo page
- ✅ Solve **Cloudflare Turnstile (standalone)** on 2Captcha's official demo page
- 🔁 (Optional) **Cloudflare Challenge** flow (needs headless browser hook to capture `cData`, `pagedata`, `action`; **off by default**)

> NOTE: These tests exercise 2Captcha itself. After they pass, wire the `TwoCaptchaClient` into your scraper and/or add similar checks around your own pages. See "Adapting to your repo" below.

## Prereqs
- Python 3.9+
- `pip install -U pytest requests playwright python-dotenv`
- Install browsers for Playwright: `python -m playwright install`
- Set your API key as env var **TWOCAPTCHA_API_KEY** (or create a `.env` file in `tests/` with it)

```bash
export TWOCAPTCHA_API_KEY=YOUR_KEY_HERE
```

Optional (for advanced Cloudflare Challenge E2E test):
- `pip install -U playwright`
- A residential proxy (if your target requires IP locality). Set `HTTP_PROXY/HTTPS_PROXY` if needed.
- Enable the optional test by setting `RUN_CF_CHALLENGE_TEST=1`

## Usage
From your repo root (or from this folder), run:
```bash
pytest -q tests
```
To run only basic smoke tests (no browser):
```bash
pytest -q -m "not e2e"
```
To run only Playwright-based E2E demo tests:
```bash
pytest -q -m e2e
```

## Adapting to your repo
1. Drop the whole `tests/` folder into your repo root (so it sits at `./tests`).  
2. If you already have a 2Captcha wrapper, update `tests/lib/two_captcha_client.py` to call your code, or add an adapter in `tests/lib/` and switch imports in the tests.
3. If your scraper runs headless and already injects tokens, mirror that logic in `tests/test_turnstile_standalone.py` so we confirm **your** injection path works.
4. CI suggestion: run `pytest -q -m "not cloudflare_challenge"` on each PR; keep the Cloudflare Challenge marked test for a manual workflow because it's flaky by nature.

## Ethics & Terms
Only run against sites you own or have explicit permission to test. Many sites (e.g., Upwork) prohibit automated login and scraping in their Terms of Service. Passing Turnstile **does not** guarantee access when Cloudflare Bot Management and device fingerprinting are present.

## Contributing & CI
- Contributor guide: see `AGENTS.md` for project structure, commands, style, and PR expectations.
- CI: GitHub Actions workflow lives at `.github/workflows/tests.yml`.
  - Smoke job runs `pytest -m smoke` on pushes/PRs to `main` (Python 3.10–3.12).
  - E2E job is optional; enable by adding repo variable `RUN_E2E=1`.
  - Add secret `TWOCAPTCHA_API_KEY` under Settings → Secrets and variables → Actions → Secrets.
