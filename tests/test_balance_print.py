import pytest


def test_print_balance(client):
    """Fetch and print the numeric 2Captcha balance."""
    bal = client.get_balance()
    print(f"\n2Captcha balance: {bal}")
    assert bal > 0.0, f"Expected positive balance, got {bal}"

