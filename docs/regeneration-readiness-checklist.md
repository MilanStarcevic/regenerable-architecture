# Regeneration Readiness Checklist

Use this checklist before discarding and regenerating a capsule's implementation. Each item
represents a failure mode: if it is not checked, the regenerated implementation may be incorrect,
incomplete, or unverifiable.

A failed checklist item is not a blocker for regeneration in all cases — but it is a risk that must
be acknowledged and addressed before or immediately after regeneration.

---

## 1. Intent

- [ ] `intent.md` accurately describes the current business purpose of the capsule
- [ ] `intent.md` states what the capsule must never get wrong
- [ ] `intent.md` reflects any business rule changes since the last review
- [ ] Domain vocabulary in `intent.md` matches current usage in the business and in tests

**Why this matters:** The regeneration recipe references `intent.md` as the primary specification. A
stale intent document produces a new implementation guided by wrong inputs.

---

## 2. Contracts

- [ ] The inbound contract (`ports/inbound/openapi.yaml`) matches the behavior the current implementation delivers
- [ ] All consumer-facing fields, error codes, and validation rules are specified in the contract
- [ ] The outbound dependencies (`ports/outbound/dependencies.yaml`) reflect the operations and fields the implementation actually uses
- [ ] Stub behaviors in the outbound declaration match the actual behavior of real dependencies

**Why this matters:** The regenerated implementation will be built to satisfy the declared
contracts. If contracts are incomplete or inaccurate, the new implementation will diverge from what
callers expect.

---

## 3. Behavioral Tests

- [ ] Acceptance tests cover all critical business behaviors
- [ ] Acceptance tests are written against the contract and intent, not against implementation details
- [ ] All acceptance tests pass against the current implementation
- [ ] Edge cases and error conditions relevant to the business are covered

**Why this matters:** Behavioral tests are the primary verification mechanism after regeneration. A
regeneration guided by weak tests produces a new implementation with undetected behavioral gaps.

---

## 4. Invariant and Contract Tests

- [ ] Invariant tests (property tests or explicit assertions) cover the rules that must hold for all inputs
- [ ] Contract tests verify that the implementation conforms to the declared inbound contract
- [ ] All invariant and contract tests pass against the current implementation

**Why this matters:** These tests catch structural regressions that acceptance tests may miss.

---

## 5. Integration Tests

- [ ] Integration tests for outbound adapters exist and target the real dependencies
- [ ] Integration tests pass against the current live dependencies
- [ ] A plan exists to re-run integration tests immediately after regeneration

**Why this matters:** Outbound adapters are disposable and will be regenerated. Integration tests
verify that the new adapter correctly interacts with the real dependency.

---

## 6. Regeneration Recipe

- [ ] `regeneration-recipe.md` is current and reflects the current artifact structure
- [ ] All files referenced in the recipe exist at the referenced paths
- [ ] The recipe has been used successfully at least once (or reviewed since the last significant change)
- [ ] The recipe specifies which model or tool to use for generation, and any known generation constraints

**Why this matters:** The recipe is the instructions. An outdated recipe will produce a generation
that misses context, references wrong files, or produces an implementation that doesn't fit the
current capsule structure.

---

## 7. Artifact Drift Fitness

- [ ] Durable health fitness has been run (Tier 1 mechanical checks)
- [ ] No Tier 1 failures are present
- [ ] LLM-assisted artifact drift checks (Tier 2) have been run if available
- [ ] No Tier 2 failures are present, or all failures are documented and accepted as known risk

**Why this matters:** Durable health fitness catches inconsistencies between artifacts that cannot
be detected from any single artifact. A high artifact drift score indicates the artifacts describe
different capsules and regeneration will fail.

---

## 8. Dependency and Consumer Impact

- [ ] Downstream consumers of this capsule have been identified (via `system.yaml`)
- [ ] Downstream consumers have been notified or their integration tests are scheduled to re-run post-regeneration
- [ ] The inbound contract version has been assessed: is this a compatible regeneration or a breaking change?
- [ ] If breaking: consumers are prepared for the change and contract versioning is in place

**Why this matters:** Regenerating a capsule that downstream capsules depend on may require their
integration tests to re-run. A regeneration that silently breaks the inbound contract breaks
consumers without warning.

---

## 9. Rollback Plan

- [ ] The current implementation is preserved (tagged, branched, or otherwise recoverable)
- [ ] The rollback trigger is defined: which test failures or operational signals indicate the regeneration should be rolled back?
- [ ] The rollback path is executable without requiring regeneration to be re-run

**Why this matters:** Regeneration can fail. The durable artifacts may be incomplete in ways the
checklist did not catch. Having a recoverable prior state limits the blast radius.

---

## Readiness Summary

| Area | Status | Notes |
|---|---|---|
| Intent | | |
| Contracts | | |
| Behavioral tests | | |
| Invariant and contract tests | | |
| Integration tests | | |
| Regeneration recipe | | |
| Durable health fitness | | |
| Consumer impact | | |
| Rollback plan | | |

Complete this table before beginning regeneration. Any unresolved item is a risk to carry forward
consciously, not an implicit assumption that it is fine.
