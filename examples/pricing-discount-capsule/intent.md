# Intent: Pricing Discount Capsule

This capsule calculates the discount percentage for a basket.

## Durable Business Intent

The durable business intent is:

- **Reward customer loyalty.** Customers with a higher tier (Gold, Silver) should receive a discount as recognition of their ongoing relationship with the business.
- **Encourage larger baskets.** Orders above a threshold basket value should receive a discount incentive for the customer to complete larger purchases.
- **Allow temporary campaign boosts.** The business can activate campaigns that add a temporary discount across all eligible orders.
- **Never exceed the maximum allowed discount.** The combined discount must be capped to protect margin. No combination of loyalty, basket, and campaign discounts may exceed the configured maximum.
- **Always explain why a discount was applied.** The response must include a human-readable list of the rules that contributed to the discount. This is required for customer-facing display, audit trails, and dispute resolution.
- **Discount must never be negative.** The capsule must not return a negative discount under any combination of inputs.

## Business Rules (at time of writing)

| Rule | Condition | Discount |
|---|---|---|
| Gold loyalty | Customer tier = Gold | +10% |
| Silver loyalty | Customer tier = Silver | +5% |
| Large basket | Basket total ≥ 500 | +3% |
| Active campaign | active_campaign = true | +2% |
| Maximum cap | Combined total ≥ 15% | capped at 15% |

These rules are subject to change. When rules change, update this document, the tests, the contract, and the regeneration recipe.

## What This Capsule Does Not Own

This capsule does not own:
- Customer records (consumed from Customer Domain API)
- Product catalog (consumed from Product Domain API)
- Campaign configuration (consumed from Campaign Domain API)

In this demo, these inputs are passed directly to the calculation function for simplicity. In a production system, the capsule would call durable domain APIs.

## This Intent Should Survive Regeneration

When this capsule is regenerated—whether due to high entropy score, a tooling upgrade, or a requirement change—this document is the source of truth for business intent.

If there is a conflict between this document and the implementation, this document is correct and the implementation should be fixed.
