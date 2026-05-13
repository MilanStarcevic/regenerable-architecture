"""
Acceptance tests for the Pricing Discount Capsule.

These tests are DURABLE. They specify what the capsule must do, expressed in
business vocabulary, independent of any implementation detail.

If the implementation is regenerated, all of these tests must continue to pass.
If a test needs to change because a business rule changed, update intent.md and
the regeneration-recipe.md at the same time.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from pricing_discount_service import calculate_discount


class TestLoyaltyDiscounts:
    def test_gold_customer_receives_ten_percent_discount(self):
        result = calculate_discount("gold", 100.0, False)
        assert result["discount_percentage"] == 10

    def test_silver_customer_receives_five_percent_discount(self):
        result = calculate_discount("silver", 100.0, False)
        assert result["discount_percentage"] == 5

    def test_unknown_tier_receives_no_loyalty_discount(self):
        result = calculate_discount("bronze", 100.0, False)
        assert result["discount_percentage"] == 0

    def test_customer_tier_is_case_insensitive(self):
        assert calculate_discount("GOLD", 100.0, False)["discount_percentage"] == 10
        assert calculate_discount("Gold", 100.0, False)["discount_percentage"] == 10
        assert calculate_discount("SILVER", 100.0, False)["discount_percentage"] == 5


class TestLargeBasketDiscount:
    def test_basket_above_threshold_receives_extra_discount(self):
        result = calculate_discount("bronze", 500.0, False)
        assert result["discount_percentage"] == 3

    def test_basket_exactly_at_threshold_receives_extra_discount(self):
        result = calculate_discount("bronze", 500.0, False)
        assert result["discount_percentage"] == 3

    def test_basket_below_threshold_receives_no_basket_discount(self):
        result = calculate_discount("bronze", 499.99, False)
        assert result["discount_percentage"] == 0

    def test_gold_customer_with_large_basket_receives_combined_discount(self):
        result = calculate_discount("gold", 600.0, False)
        assert result["discount_percentage"] == 13  # 10 + 3


class TestCampaignDiscount:
    def test_active_campaign_adds_two_percent(self):
        result = calculate_discount("bronze", 100.0, True)
        assert result["discount_percentage"] == 2

    def test_inactive_campaign_adds_nothing(self):
        result = calculate_discount("bronze", 100.0, False)
        assert result["discount_percentage"] == 0

    def test_silver_customer_with_campaign_receives_combined_discount(self):
        result = calculate_discount("silver", 100.0, True)
        assert result["discount_percentage"] == 7  # 5 + 2


class TestMaximumDiscountCap:
    def test_gold_customer_large_basket_campaign_capped_at_fifteen(self):
        # 10 + 3 + 2 = 15, exactly at cap
        result = calculate_discount("gold", 500.0, True)
        assert result["discount_percentage"] == 15

    def test_discount_cannot_exceed_fifteen_percent(self):
        result = calculate_discount("gold", 600.0, True)
        assert result["discount_percentage"] == 15

    def test_cap_explanation_included_when_applied(self):
        result = calculate_discount("gold", 600.0, True)
        explanations = " ".join(result["explanation"]).lower()
        assert "cap" in explanations or "maximum" in explanations


class TestExplanation:
    def test_explanation_lists_gold_discount_rule(self):
        result = calculate_discount("gold", 100.0, False)
        assert any("gold" in e.lower() for e in result["explanation"])

    def test_explanation_lists_silver_discount_rule(self):
        result = calculate_discount("silver", 100.0, False)
        assert any("silver" in e.lower() for e in result["explanation"])

    def test_explanation_lists_large_basket_rule(self):
        result = calculate_discount("bronze", 600.0, False)
        assert any("basket" in e.lower() or "large" in e.lower() for e in result["explanation"])

    def test_explanation_lists_campaign_rule(self):
        result = calculate_discount("bronze", 100.0, True)
        assert any("campaign" in e.lower() for e in result["explanation"])

    def test_explanation_is_empty_when_no_discount(self):
        result = calculate_discount("bronze", 100.0, False)
        assert result["explanation"] == []

    def test_explanation_lists_all_applied_rules(self):
        result = calculate_discount("gold", 600.0, True)
        text = " ".join(result["explanation"]).lower()
        assert "gold" in text
        assert "basket" in text or "large" in text
        assert "campaign" in text

    def test_discount_percentage_mentioned_in_explanation(self):
        result = calculate_discount("gold", 100.0, False)
        assert any("10%" in e or "10" in e for e in result["explanation"])

    def test_unknown_tier_returns_empty_explanation(self):
        result = calculate_discount("unknown", 100.0, False)
        assert result["explanation"] == []
