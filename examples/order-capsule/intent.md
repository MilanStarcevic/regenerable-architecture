# Intent: Order Capsule

This capsule places customer orders and applies the correct discount for the basket.

## Durable Business Intent

- **Accept order placement requests.** A customer submits a basket (items, total, tier) and the capsule records an order.
- **Apply the correct discount.** The discount is always fetched from the pricing-discount-capsule. It is never calculated inline.
- **Compute the final total.** The customer pays basket_total minus the discount amount. The final total is never negative.
- **Allow order retrieval.** A placed order can be retrieved by its order ID.
- **Preserve the discount explanation.** The explanation from the pricing-discount-capsule is stored with the order and returned to the caller. It is required for customer-facing receipts and dispute resolution.

## Business Rules

| Rule | Condition | Behaviour |
|---|---|---|
| Delegate discount | Always | Call pricing-discount-capsule; never calculate inline |
| Final total formula | Always | final_total = basket_total − (basket_total × discount_percentage ÷ 100) |
| Final total floor | final_total < 0 | Floor at 0.00 |
| Minimum one item | items is empty | Reject with error |
| Non-negative basket | basket_total < 0 | Reject with error |
| Unique order ID | Always | Each placed order receives a UUID |

## Data Ownership

Order records are **canonical data** owned by this capsule. They must survive regeneration.

In this example, orders are stored in memory. In a production system, the order store would be an external durable store (database, event log) that is independent of the implementation. Regenerating the implementation does not lose existing orders.

## What This Capsule Does Not Own

- Discount rules — delegated to the pricing-discount-capsule via its inbound port contract.
- Customer records — consumed from an external customer domain (not modelled in this example).
- Inventory — not modelled in this example.

## Outbound Dependencies

This capsule depends on the pricing-discount-capsule's `calculateDiscount` operation.
The dependency is declared in `ports/outbound/dependencies.yaml`.
Tests inject a stub that satisfies the same contract.
Integration tests (`tests/test_integration.py`) verify the real adapter against the live pricing-discount-capsule.
