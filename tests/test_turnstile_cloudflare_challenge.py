# tests/test_turnstile_cloudflare_challenge.py
"""
OPTIONAL: Cloudflare "Challenge page" flow.
- Captures cData, pagedata, action by hooking turnstile.render on a page.
- Sends them to 2Captcha with TurnstileTaskProxyless/TurnstileTask.
- Executes the callback with the returned token.

This is brittle by nature and depends on Cloudflare challenge behavior.
Enable by setting RUN_CF_CHALLENGE_TEST=1.
"""
import os
import json
import pytest

ENABLED = os.getenv("RUN_CF_CHALLENGE_TEST") == "1"

@pytest.mark.cloudflare_challenge
@pytest.mark.skipif(not ENABLED, reason="Set RUN_CF_CHALLENGE_TEST=1 to enable this test")
def test_cloudflare_challenge_flow(client):
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    target = "https://2captcha.com/demo/cloudflare-turnstile"  # If a page shows a challenge

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()  # add proxy here if needed
        page = context.new_page()

        # Inject hook to capture params
        hook = """
        () => {
            const i = setInterval(()=>{
                if (window.turnstile) {
                    clearInterval(i)
                    const orig = window.turnstile.render
                    window.turnstile.render = (a,b) => {
                        window.__CF_PARAMS__ = {
                            sitekey: b?.sitekey,
                            action: b?.action,
                            cData: b?.cData,
                            pagedata: b?.chlPageData
                        };
                        window.__TS_CALLBACK__ = b?.callback;
                        return orig(a,b);
                    }
                }
            }, 10)
        }
        """
        page.add_init_script(hook)
        page.goto(target)
        page.wait_for_timeout(3000)

        params = page.evaluate("() => window.__CF_PARAMS__ || null")
        assert params, "Could not capture Cloudflare Turnstile challenge parameters; no challenge shown?"

        task = {
            "type": "TurnstileTaskProxyless",
            "websiteURL": page.url,
            "websiteKey": params["sitekey"],
            "action": params.get("action"),
            "data": params.get("cData"),
            "pagedata": params.get("pagedata")
        }
        res = client.solve(task)
        token = (res.get("solution", {}) or {}).get("token")
        ua = (res.get("solution", {}) or {}).get("userAgent")
        assert token, f"Missing token in solution: {res}"
        assert ua, "Expected userAgent in solution for challenge flow"

        # Use returned UA for callback execution if needed
        page.evaluate("(tok) => window.__TS_CALLBACK__ && window.__TS_CALLBACK__(tok)", token)
        page.wait_for_timeout(2000)
        content = page.content().lower()
        assert ("success" in content) or ("passed" in content) or ("thank" in content), "Could not confirm success text"
        browser.close()
