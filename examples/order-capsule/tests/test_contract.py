"""
Contract tests for the Order Capsule.

These tests verify that the implementation conforms to the public API contract
defined in ports/inbound/openapi.yaml.

They are DURABLE. If the implementation is regenerated, the public API contract
must remain satisfied. If the contract changes, update openapi.yaml and update
these tests to match the new contract.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from order_service import build_order_service


def _stub_discount(tier, total, campaign):
    return {"discount_percentage": 10, "explanation": ["Gold customer discount applied: 10%"]}


@pytest.fixture
def place_order():
    svc, _ = build_order_service(_stub_discount)
    return svc


@pytest.fixture
def both(place_order):
    place_fn, get_fn = build_order_service(_stub_discount)
    return place_fn, get_fn


class TestPlaceOrderResponseSchema:
    def test_response_contains_order_id(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert "order_id" in order

    def test_response_contains_customer_tier(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert "customer_tier" in order

    def test_response_contains_basket_total(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert "basket_total" in order

    def test_response_contains_items(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert "items" in order

    def test_response_contains_active_campaign(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert "active_campaign" in order

    def test_response_contains_discount_percentage(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert "discount_percentage" in order

    def test_response_contains_discount_amount(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert "discount_amount" in order

    def test_response_contains_final_total(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert "final_total" in order

    def test_response_contains_explanation(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert "explanation" in order

    def test_response_contains_status(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert "status" in order

    def test_order_id_is_string(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert isinstance(order["order_id"], str)

    def test_discount_percentage_is_integer(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert isinstance(order["discount_percentage"], int)

    def test_discount_amount_is_float(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert isinstance(order["discount_amount"], float)

    def test_final_total_is_float(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert isinstance(order["final_total"], float)

    def test_explanation_is_list(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert isinstance(order["explanation"], list)

    def test_explanation_items_are_strings(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        for item in order["explanation"]:
            assert isinstance(item, str)

    def test_status_is_placed(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert order["status"] == "placed"

    def test_final_total_is_non_negative(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert order["final_total"] >= 0.0

    def test_discount_percentage_is_non_negative(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert order["discount_percentage"] >= 0


class TestInputValidationContract:
    def test_negative_basket_raises_error(self):
        place_order, _ = build_order_service(_stub_discount)
        with pytest.raises((ValueError, Exception)):
            place_order("gold", -1.0, False, ["item-a"])

    def test_empty_items_raises_error(self):
        place_order, _ = build_order_service(_stub_discount)
        with pytest.raises((ValueError, Exception)):
            place_order("gold", 100.0, False, [])


class TestContractExamples:
    def test_gold_customer_with_active_campaign(self):
        def campaign_discount(tier, total, campaign):
            if tier == "gold" and campaign:
                return {"discount_percentage": 12, "explanation": [
                    "Gold customer discount applied: 10%",
                    "Campaign discount applied: 2%",
                ]}
            return {"discount_percentage": 0, "explanation": []}

        place_order, _ = build_order_service(campaign_discount)
        order = place_order("gold", 200.0, True, ["widget-a", "widget-b"])
        assert order["discount_percentage"] == 12
        assert order["final_total"] == 176.0
        assert len(order["explanation"]) == 2

    def test_standard_customer_small_basket(self):
        def no_discount(tier, total, campaign):
            return {"discount_percentage": 0, "explanation": []}

        place_order, _ = build_order_service(no_discount)
        order = place_order("bronze", 50.0, False, ["widget-c"])
        assert order["discount_percentage"] == 0
        assert order["final_total"] == 50.0
        assert order["explanation"] == []
