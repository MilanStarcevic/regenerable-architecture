"""
Order Service — generated implementation.

This file is the DISPOSABLE layer of the order-capsule.
It may be regenerated when the signal dashboard indicates regeneration.

Durable artifacts that govern this implementation:
  - ../intent.md
  - ../ports/inbound/openapi.yaml
  - ../ports/outbound/dependencies.yaml
  - ../tests/test_acceptance.py
  - ../tests/test_invariants.py
  - ../regeneration-recipe.md

The discount_service parameter is the outbound port adapter.
In production it wraps the real pricing-discount-capsule.
In tests a stub satisfying the same contract is injected.
"""
from __future__ import annotations

import uuid
from typing import Callable


def build_order_service(
    discount_service: Callable[[str, float, bool], dict],
) -> tuple[Callable, Callable]:
    """
    Return (place_order, get_order) bound to isolated in-memory storage.

    discount_service must satisfy the outbound port contract declared in
    ports/outbound/dependencies.yaml: accept (customer_tier, basket_total,
    active_campaign) and return {"discount_percentage": int, "explanation": list[str]}.
    """
    _orders: dict[str, dict] = {}

    def place_order(
        customer_tier: str,
        basket_total: float,
        active_campaign: bool,
        items: list[str],
    ) -> dict:
        if basket_total < 0:
            raise ValueError("basket_total must be non-negative")
        if not items:
            raise ValueError("items must not be empty")

        discount_result = discount_service(customer_tier, basket_total, active_campaign)
        discount_pct = discount_result["discount_percentage"]
        explanation = discount_result["explanation"]

        discount_amount = round(basket_total * discount_pct / 100, 2)
        final_total = max(0.0, round(basket_total - discount_amount, 2))

        order_id = str(uuid.uuid4())
        order = {
            "order_id": order_id,
            "customer_tier": customer_tier,
            "basket_total": basket_total,
            "items": items,
            "active_campaign": active_campaign,
            "discount_percentage": discount_pct,
            "discount_amount": discount_amount,
            "final_total": final_total,
            "explanation": explanation,
            "status": "placed",
        }
        _orders[order_id] = order
        return order

    def get_order(order_id: str) -> dict | None:
        return _orders.get(order_id)

    return place_order, get_order
