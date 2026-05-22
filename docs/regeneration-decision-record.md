# Regeneration Decision Record

Fill in one record per regeneration decision. Keep completed records in version control alongside
the capsule's durable artifacts — they accumulate institutional knowledge about when and why
regeneration was warranted, and feed directly into the recipe's "Known regeneration hazards" section.

---

**Date:**
**Capsule:**
**Decision:** Proceed / Do not proceed / Postpone

---

## Trigger

Why is regeneration being considered?

Examples:
- implementation decay signals exceeded threshold
- repeated changes are becoming expensive
- dependency or framework upgrade
- implementation no longer matches intent
- current code is cheaper to replace than repair

---

## Readiness

Are the durable artifacts trustworthy enough to regenerate from?

- [ ] intent is current
- [ ] contracts are current
- [ ] tests cover expected behavior
- [ ] regeneration recipe is usable
- [ ] semantic drift has been reviewed
- [ ] no known artifact drift blocks regeneration

---

## Impact

What could be affected?

- [ ] consumers
- [ ] persisted data
- [ ] external dependencies
- [ ] security and privacy
- [ ] observability
- [ ] rollout and release risk

---

## Validation

How will we prove the regenerated capsule is acceptable?

- [ ] acceptance tests pass
- [ ] contract tests pass
- [ ] integration tests pass
- [ ] smoke test passes
- [ ] key behavior manually reviewed, if needed
- [ ] rollback path is known

---

## Notes / Lessons

What should be added back to the durable artifacts or recipe?
