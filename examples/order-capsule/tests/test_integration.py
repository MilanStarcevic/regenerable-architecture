"""
Integration tests for the order-capsule outbound adapter.

These tests verify that the real pricing-discount-capsule satisfies the outbound
port contract declared in ports/outbound/dependencies.yaml.

They cross capsule boundaries: the real calculate_discount function is used
rather than a stub. Run these separately if you want to isolate unit tests:

    pytest tests/ --ignore=tests/test_integration.py   # unit tests only
    pytest tests/test_integration.py                    # integration only
    pytest tests/                                        # all

These tests are DURABLE. They document the integration contract and will
catch regressions if the pricing-discount-capsule is regenerated with
different behaviour.
"""

import sys
import os

_pricing_src = os.path.join(
    os.path.dirname(__file__), "..", "..", "pricing-discount-capsule", "src"
)
_order_src = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, _pricing_src)
sys.path.insert(0, _order_src)

import pytest
from pricing_discount_service import calculate_discount
from order_service import build_order_service


class TestOutboundAdapterContract:
    """
    Verify the real pricing-discount-capsule satisfies the outbound port
    contract declared in ports/outbound/dependencies.yaml.

    If these fail after a regeneration of pricing-discount-capsule, the
    dependency contract must be renegotiated before order-capsule can use
    the new version safely.
    """

    def test_response_contains_discount_percentage(self):
        result = calculate_discount("gold", 100.0, False)
        assert "discount_percentage" in result

    def test_response_contains_explanation(self):
        result = calculate_discount("gold", 100.0, False)
        assert "explanation" in result

    def test_discount_percentage_is_integer(self):
        result = calculate_discount("gold", 100.0, False)
        assert isinstance(result["discount_percentage"], int)

    def test_explanation_is_list_of_strings(self):
        result = calculate_discount("gold", 100.0, False)
        assert isinstance(result["explanation"], list)
        for item in result["explanation"]:
            assert isinstance(item, str)

    def test_gold_customer_receives_ten_percent(self):
        result = calculate_discount("gold", 100.0, False)
        assert result["discount_percentage"] == 10

    def test_silver_customer_receives_five_percent(self):
        result = calculate_discount("silver", 100.0, False)
        assert result["discount_percentage"] == 5

    def test_unknown_tier_receives_zero_percent(self):
        result = calculate_discount("bronze", 50.0, False)
        assert result["discount_percentage"] == 0

    def test_discount_is_non_negative(self):
        result = calculate_discount("bronze", 0.0, False)
        assert result["discount_percentage"] >= 0


class TestEndToEndWithRealDiscountCapsule:
    """
    Full order placement using the real pricing-discount-capsule.
    Exercises the complete integration path.
    """

    @pytest.fixture
    def service(self):
        return build_order_service(calculate_discount)

    def test_gold_customer_order_applies_correct_discount(self, service):
        place_order, _ = service
        order = place_order("gold", 100.0, False, ["item-a"])
        assert order["discount_percentage"] == 10
        assert order["final_total"] == 90.0

    def test_silver_customer_order_applies_correct_discount(self, service):
        place_order, _ = service
        order = place_order("silver", 100.0, False, ["item-a"])
        assert order["discount_percentage"] == 5
        assert order["final_total"] == 95.0

    def test_explanation_from_real_capsule_is_preserved(self, service):
        place_order, _ = service
        order = place_order("gold", 100.0, False, ["item-a"])
        assert any("Gold" in line for line in order["explanation"])

    def test_placed_order_is_retrievable(self, service):
        place_order, get_order = service
        order = place_order("silver", 200.0, False, ["item-a", "item-b"])
        retrieved = get_order(order["order_id"])
        assert retrieved["order_id"] == order["order_id"]
        assert retrieved["discount_percentage"] == 5

    def test_campaign_flag_forwarded_to_discount_capsule(self, service):
        place_order, _ = service
        order_no_campaign = place_order("bronze", 100.0, False, ["item-a"])
        order_with_campaign = place_order("bronze", 100.0, True, ["item-a"])
        assert order_with_campaign["discount_percentage"] == order_no_campaign["discount_percentage"] + 2
