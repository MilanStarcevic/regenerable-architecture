"""
Acceptance tests for the Order Capsule.

These tests are DURABLE. They specify what the capsule must do, expressed in
business vocabulary, independent of any implementation detail.

A stub discount service is injected to isolate this capsule from the
pricing-discount-capsule. The stub satisfies the outbound port contract
declared in ports/outbound/dependencies.yaml.

If the implementation is regenerated, all of these tests must continue to pass.
If a business rule changes, update intent.md and regeneration-recipe.md too.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from order_service import build_order_service


def _stub_discount(customer_tier: str, basket_total: float, active_campaign: bool) -> dict:
    """Stub satisfying the outbound port contract (ports/outbound/dependencies.yaml)."""
    tier = customer_tier.lower()
    if tier == "gold":
        return {"discount_percentage": 10, "explanation": ["Gold customer discount applied: 10%"]}
    if tier == "silver":
        return {"discount_percentage": 5, "explanation": ["Silver customer discount applied: 5%"]}
    return {"discount_percentage": 0, "explanation": []}


@pytest.fixture
def service():
    return build_order_service(_stub_discount)


@pytest.fixture
def place_order(service):
    return service[0]


@pytest.fixture
def get_order(service):
    return service[1]


class TestOrderPlacement:
    def test_gold_customer_receives_ten_percent_discount(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert order["discount_percentage"] == 10

    def test_silver_customer_receives_five_percent_discount(self, place_order):
        order = place_order("silver", 100.0, False, ["item-a"])
        assert order["discount_percentage"] == 5

    def test_unknown_tier_receives_no_discount(self, place_order):
        order = place_order("bronze", 100.0, False, ["item-a"])
        assert order["discount_percentage"] == 0

    def test_final_total_reflects_discount(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert order["final_total"] == 90.0

    def test_final_total_for_no_discount(self, place_order):
        order = place_order("bronze", 50.0, False, ["item-a"])
        assert order["final_total"] == 50.0

    def test_discount_amount_is_correct(self, place_order):
        order = place_order("gold", 200.0, False, ["item-a"])
        assert order["discount_amount"] == 20.0

    def test_order_contains_all_required_fields(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        required = {
            "order_id", "customer_tier", "basket_total", "items",
            "active_campaign", "discount_percentage", "discount_amount",
            "final_total", "explanation", "status",
        }
        assert required.issubset(order.keys())

    def test_order_status_is_placed(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert order["status"] == "placed"

    def test_explanation_from_discount_service_is_preserved(self, place_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        assert "Gold customer discount applied: 10%" in order["explanation"]

    def test_empty_explanation_preserved_for_no_discount(self, place_order):
        order = place_order("bronze", 50.0, False, ["item-a"])
        assert order["explanation"] == []

    def test_items_are_stored_on_order(self, place_order):
        order = place_order("gold", 100.0, False, ["widget-a", "widget-b"])
        assert order["items"] == ["widget-a", "widget-b"]

    def test_campaign_flag_is_stored_on_order(self, place_order):
        order = place_order("bronze", 50.0, True, ["item-a"])
        assert order["active_campaign"] is True


class TestOrderRetrieval:
    def test_placed_order_can_be_retrieved_by_id(self, place_order, get_order):
        order = place_order("gold", 100.0, False, ["item-a"])
        retrieved = get_order(order["order_id"])
        assert retrieved == order

    def test_unknown_order_id_returns_none(self, get_order):
        assert get_order("nonexistent-id") is None

    def test_each_order_gets_unique_id(self, place_order):
        order1 = place_order("gold", 100.0, False, ["item-a"])
        order2 = place_order("gold", 100.0, False, ["item-b"])
        assert order1["order_id"] != order2["order_id"]

    def test_multiple_orders_are_stored_independently(self, place_order, get_order):
        order1 = place_order("gold", 100.0, False, ["item-a"])
        order2 = place_order("silver", 200.0, True, ["item-b", "item-c"])
        assert get_order(order1["order_id"])["discount_percentage"] == 10
        assert get_order(order2["order_id"])["discount_percentage"] == 5


class TestDiscountDelegation:
    def test_campaign_flag_is_forwarded_to_discount_service(self):
        forwarded_args = []

        def recording_discount(tier, total, campaign):
            forwarded_args.append((tier, total, campaign))
            return {"discount_percentage": 0, "explanation": []}

        place_order, _ = build_order_service(recording_discount)
        place_order("bronze", 50.0, True, ["item-a"])
        assert forwarded_args == [("bronze", 50.0, True)]

    def test_customer_tier_is_forwarded_to_discount_service(self):
        forwarded_tiers = []

        def recording_discount(tier, total, campaign):
            forwarded_tiers.append(tier)
            return {"discount_percentage": 0, "explanation": []}

        place_order, _ = build_order_service(recording_discount)
        place_order("gold", 50.0, False, ["item-a"])
        assert forwarded_tiers == ["gold"]

    def test_discount_service_is_called_exactly_once_per_order(self):
        call_count = [0]

        def counting_discount(tier, total, campaign):
            call_count[0] += 1
            return {"discount_percentage": 0, "explanation": []}

        place_order, _ = build_order_service(counting_discount)
        place_order("bronze", 50.0, False, ["item-a"])
        assert call_count[0] == 1
