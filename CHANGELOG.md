# Changelog

All notable changes to this project will be documented here.

## [Unreleased]
- Add contributor guide `AGENTS.md` with setup, style, and security tips.
- Register pytest markers via `pytest.ini` (`smoke`, `e2e`, `cloudflare_challenge`).
- Reclassify slow token-solve tests from `smoke` to `e2e` to keep smoke fast.
- Add `tests/test_balance_print.py` to print numeric 2Captcha balance.
- Update `README.md` to use `pytest -m smoke` and document balance print.

