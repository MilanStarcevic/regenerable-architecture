"""
Invariant tests for the Order Capsule.

These tests are DURABLE. They express rules that must hold for ALL inputs,
regardless of how the implementation is structured.

Invariants are the last line of defence before regeneration: if these pass
after regeneration and acceptance tests pass, the capsule is correct.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from order_service import build_order_service


def _fixed_discount(pct: int):
    def _discount(tier, total, campaign):
        return {"discount_percentage": pct, "explanation": [f"Fixed {pct}% discount"]}
    return _discount


class TestFinalTotalInvariants:
    def test_final_total_is_never_negative(self):
        place_order, _ = build_order_service(_fixed_discount(100))
        order = place_order("gold", 50.0, False, ["item-a"])
        assert order["final_total"] >= 0.0

    def test_final_total_is_never_negative_for_extreme_discount(self):
        place_order, _ = build_order_service(_fixed_discount(100))
        order = place_order("bronze", 0.01, False, ["item-a"])
        assert order["final_total"] >= 0.0

    def test_final_total_with_zero_discount_equals_basket_total(self):
        place_order, _ = build_order_service(_fixed_discount(0))
        order = place_order("bronze", 99.99, False, ["item-a"])
        assert order["final_total"] == 99.99

    def test_final_total_plus_discount_amount_equals_basket_total(self):
        place_order, _ = build_order_service(_fixed_discount(10))
        order = place_order("gold", 100.0, False, ["item-a"])
        assert round(order["final_total"] + order["discount_amount"], 10) == order["basket_total"]


class TestInputValidationInvariants:
    def test_empty_items_raises_error(self):
        place_order, _ = build_order_service(_fixed_discount(0))
        with pytest.raises(ValueError):
            place_order("gold", 100.0, False, [])

    def test_negative_basket_raises_error(self):
        place_order, _ = build_order_service(_fixed_discount(0))
        with pytest.raises(ValueError):
            place_order("gold", -1.0, False, ["item-a"])

    def test_zero_basket_total_is_accepted(self):
        place_order, _ = build_order_service(_fixed_discount(0))
        order = place_order("bronze", 0.0, False, ["item-a"])
        assert order["final_total"] == 0.0
        assert order["discount_amount"] == 0.0


class TestDiscountApplicationInvariants:
    def test_discount_is_applied_exactly_once(self):
        call_count = [0]

        def counting_discount(tier, total, campaign):
            call_count[0] += 1
            return {"discount_percentage": 10, "explanation": []}

        place_order, _ = build_order_service(counting_discount)
        place_order("gold", 100.0, False, ["item-a"])
        assert call_count[0] == 1

    def test_stored_discount_matches_what_service_returned(self):
        def specific_discount(tier, total, campaign):
            return {"discount_percentage": 7, "explanation": ["Special 7%"]}

        place_order, get_order = build_order_service(specific_discount)
        order = place_order("gold", 100.0, False, ["item-a"])
        retrieved = get_order(order["order_id"])
        assert retrieved["discount_percentage"] == 7
