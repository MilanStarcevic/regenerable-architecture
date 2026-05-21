# Capability Capsule Assessment Checklist

Use this checklist when proposing or reviewing a new capability capsule boundary. The goal is to
assess whether the boundary is well-defined enough to support the Regenerable Architecture
lifecycle.

A capsule that fails these checks is not ready. The failure identifies what needs to be resolved
before the capsule can be safely specified, generated, operated, and regenerated.

---

## 1. Capability Clarity

- [ ] The capsule's business purpose can be stated in a single, clear paragraph
- [ ] A competent domain expert would agree with that statement
- [ ] The capsule's name reflects what it *does*, not what it *is* or how it is *built*
- [ ] The capsule has a clear statement of what it must never get wrong

**Failure mode:** If the purpose cannot be stated clearly, the intent document will be ambiguous,
and the regenerated implementation will reflect that ambiguity.

---

## 2. Boundary Stability

- [ ] The capsule boundary reflects a stable business capability, not a current implementation convenience
- [ ] The boundary is unlikely to split or merge under foreseeable business change
- [ ] The boundary is not drawn to match an existing codebase structure that may itself need to change

**Failure mode:** Unstable boundaries require constant restructuring of durable artifacts. The
overhead exceeds the value of the pattern.

---

## 3. Ownership

- [ ] There is a named owner (person or team) for the durable artifacts
- [ ] The owner has authority to define the inbound contract
- [ ] The owner has accountability for maintaining intent, tests, and the regeneration recipe as the domain evolves
- [ ] The owner understands that maintaining the durable layer is as important as maintaining the implementation

**Failure mode:** Without ownership, durable artifacts decay. Neglected artifacts lead to
regenerations guided by wrong inputs (see [anti-patterns.md — Durable Artifact
Neglect](anti-patterns.md)).

---

## 4. Inbound Contract Viability

- [ ] The capsule's public API can be defined before the implementation is written
- [ ] Callers can commit to using the API as defined, without implementation-level coupling
- [ ] The inbound contract is stable enough to version and publish to consumers
- [ ] The API surface is the smallest it can be while still fulfilling the capability

**Failure mode:** An inbound contract that cannot be defined before implementation suggests the
boundary is wrong, or the capability is not well-understood enough to capsule.

---

## 5. Outbound Dependency Explicitness

- [ ] Current dependencies this capsule will consume are identified
- [ ] The specific operations and response fields the capsule will use are known
- [ ] Each dependency is itself a declared capsule or a stable external service with a defined interface
- [ ] Stub behaviors for dependencies can be defined for testing purposes

**Failure mode:** Implicit or uncontrolled outbound dependencies mean the capsule cannot be tested
in isolation and cannot be safely regenerated when dependencies evolve.

---

## 6. Data Classification

- [ ] All data the capsule will own or consume is classified (canonical, derived, ephemeral, audit, configuration, personal/sensitive)
- [ ] Canonical data is owned by a durable domain API, not by this capsule's disposable implementation
- [ ] The capsule's data lifecycle is compatible with its regeneration lifecycle

**Failure mode:** A capsule whose disposable implementation owns canonical data will lose that data
on regeneration (see [anti-patterns.md — Distributed Data Ownership](anti-patterns.md) and
[data-strategies.md](data-strategies.md)).

---

## 7. Behavioral Testability

- [ ] The critical business behaviors can be expressed as acceptance tests against the inbound contract
- [ ] Those tests can be run without the real implementations of outbound dependencies (using stubs)
- [ ] The tests would detect a behavioral regression introduced by a fresh regeneration

**Failure mode:** If behavioral tests cannot be written before the implementation exists, the
capsule's intent is not well-enough understood to generate correctly.

---

## 8. Regenerability

- [ ] A competent engineer (or AI tool given the durable artifacts) could recreate the implementation correctly without the current code
- [ ] The regeneration recipe can be written in concrete steps, not vague intentions
- [ ] The capsule is not so entangled with adjacent capsules that regenerating it requires simultaneous changes to others

**Failure mode:** A capsule that cannot be regenerated independently cannot benefit from the
regeneration lifecycle. This often indicates that the boundary is wrong.

---

## 9. Deployment Justification

- [ ] If this capsule will be deployed as a service: the isolation justifies the operational overhead (see [anti-patterns.md — Nano-Service Explosion](anti-patterns.md))
- [ ] If this capsule will be a module in a monolith: the boundary is enforced at the code level (import rules, package structure)
- [ ] The deployment decision is not driving the boundary decision

**Failure mode:** When deployment topology drives capsule boundaries, the result is either
under-decomposition (too little isolation) or over-decomposition (nano-services) for the wrong
reasons.

---

## Assessment Summary

| Dimension | Status | Notes |
|---|---|---|
| Capability clarity | | |
| Boundary stability | | |
| Ownership | | |
| Inbound contract viability | | |
| Outbound dependency explicitness | | |
| Data classification | | |
| Behavioral testability | | |
| Regenerability | | |
| Deployment justification | | |

A proposed capsule with multiple unresolved items needs more design work before the first artifact
is written. Resolve the failures first — they will shape the intent document, the contracts, and the
regeneration recipe.
