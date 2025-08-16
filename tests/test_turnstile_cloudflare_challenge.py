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

    # Allow overriding the target to a page that reliably shows a CF challenge
    target = os.getenv("CF_CHALLENGE_URL", "https://2captcha.com/demo/cloudflare-turnstile")

    headful = os.getenv("HEADFUL") == "1"
    wait_ms = int(os.getenv("CF_WAIT_MS", "5000"))
    skip_if_none = os.getenv("SKIP_IF_NO_CHALLENGE") == "1"

    with sync_playwright() as p:
        # Optional proxy for increasing challenge likelihood; format: http(s)://user:pass@host:port
        proxy_url = os.getenv("PLAYWRIGHT_PROXY")
        launch_kwargs = {"headless": not headful}
        if proxy_url:
            try:
                from urllib.parse import urlparse
                u = urlparse(proxy_url)
                server = f"{u.scheme}://{u.hostname}:{u.port}" if u.hostname and u.port else f"{u.scheme}://{u.hostname}"
                proxy_cfg = {"server": server}
                if u.username:
                    proxy_cfg["username"] = u.username
                if u.password:
                    proxy_cfg["password"] = u.password
                launch_kwargs["proxy"] = proxy_cfg
            except Exception:
                pass

        browser = p.chromium.launch(**launch_kwargs)
        context = browser.new_context()
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
        page.wait_for_timeout(wait_ms)

        params = page.evaluate("() => window.__CF_PARAMS__ || null")
        if not params and skip_if_none:
            pytest.skip("No CF challenge shown; skipping per SKIP_IF_NO_CHALLENGE=1")
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
