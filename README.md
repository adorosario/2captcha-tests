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
pytest -q -m smoke
```
To run only Playwright-based E2E demo tests:
```bash
pytest -q -m e2e
```

To print your current 2Captcha balance under pytest:
```bash
pytest -q -s tests/test_balance_print.py
```

### Cloudflare Challenge Options (optional/brittle)
Environment toggles to help reproduce a challenge:
- `RUN_CF_CHALLENGE_TEST=1`: enable the challenge test.
- `HEADFUL=1`: run Chromium headful (requires X or use `xvfb-run`).
- `CF_CHALLENGE_URL=https://your-page.example`: override target URL.
- `PLAYWRIGHT_PROXY=http://user:pass@host:port`: route via proxy.
- `CF_WAIT_MS=12000`: wait longer for params capture.
- `SKIP_IF_NO_CHALLENGE=1`: skip instead of fail when no challenge is shown.
- Device fingerprint (optional):
  - `PLAYWRIGHT_DEVICE="Pixel 7"` (or any Playwright device name)
  - `CF_USER_AGENT="...Chrome/124..."`
  - `CF_LOCALE=en-US` (also sets `Accept-Language` header)
  - `CF_TIMEZONE=America/New_York`
  - `CF_VIEWPORT=1280x800` `CF_DPR=1.0` `CF_MOBILE=1` `CF_HAS_TOUCH=1`

Example in Docker (headful via virtual display):
```bash
docker compose run --rm e2e bash -lc 'export RUN_CF_CHALLENGE_TEST=1 HEADFUL=1 CF_WAIT_MS=8000; xvfb-run -a pytest -m cloudflare_challenge -q'
```

Example with proxy + device:
```bash
docker compose run --rm e2e bash -lc '
  export RUN_CF_CHALLENGE_TEST=1 \
         CF_WAIT_MS=12000 \
         SKIP_IF_NO_CHALLENGE=1 \
         CF_CHALLENGE_URL=https://your-page.example \
         PLAYWRIGHT_PROXY=http://user:pass@res-proxy:port \
         PLAYWRIGHT_DEVICE="Pixel 7" \
         CF_LOCALE=en-US CF_TIMEZONE=America/New_York; \
  xvfb-run -a pytest -m cloudflare_challenge -q'
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
