"""
Pricing Discount Service — generated implementation.

This file is the DISPOSABLE layer of the pricing-discount-capsule.
It may be regenerated when the entropy score exceeds the configured threshold.

Durable artifacts that govern this implementation:
  - ../intent.md
  - ../ports/inbound/openapi.yaml
  - ../ports/outbound/dependencies.yaml
  - ../tests/test_acceptance.py
  - ../tests/test_invariants.py
  - ../regeneration-recipe.md
"""
from __future__ import annotations

GOLD_DISCOUNT = 10
SILVER_DISCOUNT = 5
LARGE_BASKET_DISCOUNT = 3
CAMPAIGN_DISCOUNT = 2
LARGE_BASKET_THRESHOLD = 500.0
MAX_DISCOUNT = 15


def calculate_discount(
    customer_tier: str,
    basket_total: float,
    active_campaign: bool,
) -> dict:
    """Return discount_percentage (0-15) and explanation list for a basket."""
    if basket_total < 0:
        raise ValueError("basket_total must be non-negative")

    discount = 0
    explanation: list[str] = []

    tier = customer_tier.lower()
    if tier == "gold":
        discount += GOLD_DISCOUNT
        explanation.append(f"Gold customer discount applied: {GOLD_DISCOUNT}%")
    elif tier == "silver":
        discount += SILVER_DISCOUNT
        explanation.append(f"Silver customer discount applied: {SILVER_DISCOUNT}%")

    if basket_total >= LARGE_BASKET_THRESHOLD:
        discount += LARGE_BASKET_DISCOUNT
        explanation.append(f"Large basket discount applied: {LARGE_BASKET_DISCOUNT}%")

    if active_campaign:
        discount += CAMPAIGN_DISCOUNT
        explanation.append(f"Campaign discount applied: {CAMPAIGN_DISCOUNT}%")

    if discount >= MAX_DISCOUNT:
        explanation.append(f"Maximum discount cap applied: {MAX_DISCOUNT}%")
        discount = MAX_DISCOUNT

    return {
        "discount_percentage": discount,
        "explanation": explanation,
    }
