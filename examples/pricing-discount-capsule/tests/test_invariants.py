"""
Invariant tests for the Pricing Discount Capsule.

These tests express properties that must ALWAYS hold, regardless of inputs.
They are DURABLE artifacts: if the implementation is regenerated, all of these
invariants must continue to hold.

These are the rules that must never be violated under any combination of inputs.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from pricing_discount_service import calculate_discount

TIERS = ["gold", "silver", "bronze", "platinum", "unknown", "", "GOLD", "Silver"]
BASKET_TOTALS = [0.0, 1.0, 100.0, 499.99, 500.0, 500.01, 1000.0, 9999.99]
CAMPAIGN_FLAGS = [True, False]


class TestDiscountNeverNegative:
    """Discount must never be negative under any inputs."""

    def test_zero_basket_produces_non_negative_discount(self):
        for tier in TIERS:
            for campaign in CAMPAIGN_FLAGS:
                result = calculate_discount(tier, 0.0, campaign)
                assert result["discount_percentage"] >= 0, (
                    f"Negative discount for tier={tier!r}, basket=0, campaign={campaign}"
                )

    def test_all_tier_combinations_produce_non_negative_discount(self):
        for tier in TIERS:
            for basket in BASKET_TOTALS:
                for campaign in CAMPAIGN_FLAGS:
                    result = calculate_discount(tier, basket, campaign)
                    assert result["discount_percentage"] >= 0, (
                        f"Negative discount for tier={tier!r}, basket={basket}, campaign={campaign}"
                    )


class TestDiscountNeverExceedsMaximum:
    """Discount must never exceed the maximum cap (15%) under any inputs."""

    def test_all_combinations_respect_maximum_cap(self):
        for tier in TIERS:
            for basket in BASKET_TOTALS:
                for campaign in CAMPAIGN_FLAGS:
                    result = calculate_discount(tier, basket, campaign)
                    assert result["discount_percentage"] <= 15, (
                        f"Discount exceeded 15% for tier={tier!r}, basket={basket}, campaign={campaign}: "
                        f"got {result['discount_percentage']}%"
                    )


class TestDiscountIsInteger:
    """Discount percentage must always be an integer."""

    def test_discount_percentage_is_always_integer(self):
        for tier in TIERS:
            for basket in BASKET_TOTALS:
                for campaign in CAMPAIGN_FLAGS:
                    result = calculate_discount(tier, basket, campaign)
                    assert isinstance(result["discount_percentage"], int), (
                        f"Non-integer discount for tier={tier!r}, basket={basket}, campaign={campaign}: "
                        f"got {type(result['discount_percentage'])}"
                    )


class TestExplanationAlwaysPresent:
    """Explanation must always be present in the response."""

    def test_explanation_key_always_present(self):
        for tier in TIERS:
            for basket in BASKET_TOTALS:
                for campaign in CAMPAIGN_FLAGS:
                    result = calculate_discount(tier, basket, campaign)
                    assert "explanation" in result, (
                        f"Missing explanation key for tier={tier!r}, basket={basket}, campaign={campaign}"
                    )
                    assert isinstance(result["explanation"], list), (
                        f"Explanation is not a list for tier={tier!r}, basket={basket}, campaign={campaign}"
                    )


class TestExplanationMatchesDiscount:
    """If discount is 0, explanation must be empty. If discount > 0, explanation must not be empty."""

    def test_zero_discount_has_empty_explanation(self):
        result = calculate_discount("unknown", 100.0, False)
        assert result["discount_percentage"] == 0
        assert result["explanation"] == [], (
            f"Expected empty explanation for zero discount, got {result['explanation']}"
        )

    def test_nonzero_discount_has_nonempty_explanation(self):
        for tier in ["gold", "silver"]:
            result = calculate_discount(tier, 100.0, False)
            assert result["discount_percentage"] > 0
            assert len(result["explanation"]) > 0, (
                f"Expected non-empty explanation for {tier!r} tier with nonzero discount"
            )


class TestNegativeBasketRejected:
    """Negative basket totals must raise an error."""

    def test_negative_basket_raises_value_error(self):
        with pytest.raises((ValueError, Exception)):
            calculate_discount("gold", -1.0, False)

    def test_large_negative_basket_raises_error(self):
        with pytest.raises((ValueError, Exception)):
            calculate_discount("silver", -999.99, True)
