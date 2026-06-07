import pytest

from orderkit import line_total, cart_total


def test_line_total_basic():
    assert line_total(20, 3) == 60.0
    assert line_total(20, 3, 0.1) == 54.0


def test_line_total_rounds():
    assert line_total(0.1, 3) == 0.3          # 0.30000000000000004 -> 0.3
    assert line_total(9.99, 2, 0.05) == 18.98  # round(19.98*0.95, 2)


def test_line_total_validates():
    with pytest.raises(ValueError):
        line_total(-1, 1)
    with pytest.raises(ValueError):
        line_total(1, -1)
    with pytest.raises(ValueError):
        line_total(1, 1, 1.0)


def test_cart_total():
    cart = [
        {"price": 20, "qty": 3},
        {"price": 50, "qty": 1, "discount": 0.2},
    ]
    assert cart_total(cart) == 100.0
