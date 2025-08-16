# tests/conftest.py
import os
import pytest
from dotenv import load_dotenv
from tests.lib.two_captcha_client import TwoCaptchaClient, TwoCaptchaError

# Load .env if present
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=False)

def pytest_addoption(parser):
    parser.addoption("--twocaptcha-key", action="store", default=None, help="Override TWOCAPTCHA_API_KEY")

@pytest.fixture(scope="session")
def api_key(pytestconfig):
    key = pytestconfig.getoption("--twocaptcha-key") or os.getenv("TWOCAPTCHA_API_KEY")
    if not key:
        pytest.skip("TWOCAPTCHA_API_KEY not set; skipping 2Captcha tests")
    return key

@pytest.fixture(scope="session")
def client(api_key):
    return TwoCaptchaClient(api_key=api_key)

@pytest.fixture(scope="session")
def has_balance(client):
    try:
        bal = client.get_balance()
    except TwoCaptchaError:
        return False
    return bal and bal > 0.001
