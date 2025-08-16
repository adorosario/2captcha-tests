# tests/test_balance.py
import pytest

@pytest.mark.smoke
def test_balance_available(client, has_balance):
    assert has_balance, "Account balance is zero/low or API unreachable"
    bal = client.get_balance()
    assert bal > 0, f"Expected positive balance, got {bal}"
