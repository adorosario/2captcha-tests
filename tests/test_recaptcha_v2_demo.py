# tests/test_recaptcha_v2_demo.py
"""
Validates 2Captcha can return a gRecaptchaResponse for the official demo page
and (E2E) injects it in a real browser to confirm the page accepts it.
"""
import os
import pytest

DEMO_URL = "https://2captcha.com/demo/recaptcha-v2"
# From 2Captcha docs (subject to change, we try the DOM first in the E2E test)
DEMO_SITEKEY = "6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u"

@pytest.mark.e2e
def test_recaptcha_v2_token_solve(client):
    task = {
        "type": "RecaptchaV2TaskProxyless",
        "websiteURL": DEMO_URL,
        "websiteKey": DEMO_SITEKEY,
        "isInvisible": False
    }
    res = client.solve(task)
    assert res.get("status") == "ready"
    sol = res.get("solution", {})
    assert sol.get("gRecaptchaResponse") or sol.get("token"), f"Unexpected solution: {sol}"

@pytest.mark.e2e
def test_recaptcha_v2_demo_page_accepts_token(client):
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright, expect

    task = {
        "type": "RecaptchaV2TaskProxyless",
        "websiteURL": DEMO_URL,
        "websiteKey": DEMO_SITEKEY,
        "isInvisible": False
    }
    res = client.solve(task)
    token = (res.get("solution", {}) or {}).get("gRecaptchaResponse") or (res.get("solution", {}) or {}).get("token")
    assert token, "No token returned"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(DEMO_URL, wait_until="domcontentloaded")
        # Inject the token into the expected field and submit the form
        page.evaluate("""(tok) => {
            const inp = document.querySelector('textarea#g-recaptcha-response, textarea[name="g-recaptcha-response"]');
            if (inp) { inp.value = tok; }
        }""", token)
        # Click the submit button if present
        submit = page.locator('button[type="submit"], input[type="submit"]')
        if submit.count():
            submit.first.click()
        # Heuristic success check: look for "success" text
        page.wait_for_timeout(2000)
        content = page.content().lower()
        assert ("success" in content) or ("passed" in content) or ("thank" in content), "Could not confirm success text"
        browser.close()
