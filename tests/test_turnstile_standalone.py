# tests/test_turnstile_standalone.py
"""
Validates 2Captcha solves Cloudflare Turnstile (standalone widget) on the official demo page.
"""
import pytest

DEMO_URL = "https://2captcha.com/demo/cloudflare-turnstile"
# As per docs, public test sitekey is 3x00000000000000000000FF for Turnstile demo pages.
DEMO_SITEKEY = "3x00000000000000000000FF"

@pytest.mark.e2e
def test_turnstile_token_solve(client):
    task = {
        "type": "TurnstileTaskProxyless",
        "websiteURL": DEMO_URL,
        "websiteKey": DEMO_SITEKEY
    }
    res = client.solve(task)
    assert res.get("status") == "ready"
    sol = res.get("solution", {})
    assert sol.get("token"), f"Unexpected solution: {sol}"

@pytest.mark.e2e
def test_turnstile_demo_page_accepts_token(client):
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    task = {
        "type": "TurnstileTaskProxyless",
        "websiteURL": DEMO_URL,
        "websiteKey": DEMO_SITEKEY
    }
    res = client.solve(task)
    token = (res.get("solution", {}) or {}).get("token")
    assert token, "No token returned"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(DEMO_URL, wait_until="domcontentloaded")
        # Insert token into cf-turnstile-response (or the reCAPTCHA-compatible name)
        page.evaluate("""(tok) => {
            const inp =
              document.querySelector('input[name="cf-turnstile-response"]') ||
              document.querySelector('textarea[name="g-recaptcha-response"]');
            if (inp) { inp.value = tok; }
        }""", token)
        # Try to submit if button present
        submit = page.locator('button[type="submit"], input[type="submit"]')
        if submit.count():
            submit.first.click()
        page.wait_for_timeout(2000)
        txt = page.content().lower()
        assert ("success" in txt) or ("passed" in txt) or ("thank" in txt), "Could not confirm success text"
        browser.close()
