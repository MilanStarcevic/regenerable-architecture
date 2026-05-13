"""
Contract tests for the Pricing Discount Capsule.

These tests verify that the implementation conforms to the public API contract
defined in contracts/openapi.yaml.

They are DURABLE. If the implementation is regenerated, the public API contract
must remain satisfied. If the contract changes, update openapi.yaml and update
these tests to match the new contract.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from pricing_discount_service import calculate_discount


class TestResponseSchema:
    """Verify the response always matches the documented schema."""

    def test_response_contains_required_discount_percentage_key(self):
        result = calculate_discount("gold", 100.0, False)
        assert "discount_percentage" in result

    def test_response_contains_required_explanation_key(self):
        result = calculate_discount("gold", 100.0, False)
        assert "explanation" in result

    def test_response_has_no_extra_unexpected_keys(self):
        result = calculate_discount("gold", 100.0, False)
        allowed_keys = {"discount_percentage", "explanation"}
        unexpected = set(result.keys()) - allowed_keys
        assert not unexpected, f"Unexpected keys in response: {unexpected}"

    def test_discount_percentage_is_integer_type(self):
        result = calculate_discount("silver", 200.0, True)
        assert isinstance(result["discount_percentage"], int)

    def test_explanation_is_list_type(self):
        result = calculate_discount("gold", 200.0, False)
        assert isinstance(result["explanation"], list)

    def test_explanation_items_are_strings(self):
        result = calculate_discount("gold", 200.0, True)
        for item in result["explanation"]:
            assert isinstance(item, str), f"Non-string explanation item: {item!r}"


class TestDiscountBounds:
    """Verify discount_percentage stays within the bounds declared in the contract."""

    def test_discount_minimum_is_zero(self):
        result = calculate_discount("unknown", 10.0, False)
        assert result["discount_percentage"] >= 0

    def test_discount_maximum_is_fifteen(self):
        result = calculate_discount("gold", 600.0, True)
        assert result["discount_percentage"] <= 15


class TestContractExamples:
    """Verify the contract examples from openapi.yaml produce correct results."""

    def test_gold_customer_large_basket_active_campaign(self):
        # From openapi.yaml example: gold, 600.00, active_campaign=True
        # 10 + 3 + 2 = 15, capped at 15
        result = calculate_discount("gold", 600.00, True)
        assert result["discount_percentage"] == 15
        assert len(result["explanation"]) > 0

    def test_silver_customer_small_basket_no_campaign(self):
        # From openapi.yaml example: silver, 100.00, active_campaign=False
        # 5 + 0 + 0 = 5
        result = calculate_discount("silver", 100.00, False)
        assert result["discount_percentage"] == 5

    def test_unknown_tier_small_basket_no_campaign(self):
        # From openapi.yaml example: bronze, 50.00, active_campaign=False
        # 0 + 0 + 0 = 0
        result = calculate_discount("bronze", 50.00, False)
        assert result["discount_percentage"] == 0
        assert result["explanation"] == []


class TestInputValidation:
    """Verify input validation matches the contract."""

    def test_negative_basket_total_raises_error(self):
        with pytest.raises((ValueError, Exception)):
            calculate_discount("gold", -1.0, False)
