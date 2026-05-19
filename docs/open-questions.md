# Open Questions

These questions do not have settled answers. They are worth working through before applying the
pattern at scale, because the decisions made here determine whether the lifecycle actually functions
in practice or just looks good on paper.

---

## 1. How do fitness function thresholds evolve as systems mature?

Initial thresholds are calibrated against a naive baseline. As teams progress through the adoption
maturity levels, their baseline shifts. Should thresholds tighten over time?

A team that consistently achieves an entropy score of 10 should probably recalibrate their threshold
from 50 to 25 — otherwise the fitness function loses its signal. The adoption maturity model
([docs/adoption-maturity-model.md](adoption-maturity-model.md)) describes the advancement signals,
but does not prescribe threshold recalibration.

**Still open for architects:**

- Should thresholds be absolute values or relative to a capsule's historical baseline?
- Who owns the threshold calibration decision — the capsule owner, the architecture team, or a
  central governance body?


## 2. When does a capsule's data ownership become load-bearing?

**Partially addressed.** The `system.yaml` now classifies data as canonical, derived, or ephemeral
per capsule. The data strategies doc ([docs/data-strategies.md](data-strategies.md)) covers
ownership patterns.

**Still open for architects:**

- Some capsules start as experiments and accumulate canonical data over time. At what point does the
  data classification require a formal review? What triggers the escalation from "derived" to
  "canonical"?
- How do you migrate canonical data ownership from a disposable capsule to a durable domain API
  without disrupting consumers?
- The `lifecycle_level` field in `system.yaml` tracks adoption maturity but does not encode data
  durability requirements. A Level 1 capsule that has accumulated canonical data is in an unsafe
  state that the manifest alone cannot flag.


## 3. What does regenerable architecture add beyond rigorous TDD?

Strong behavioral tests are a prerequisite for safe regeneration. A well-tested capsule with explicit
contracts is already close to regenerable. The question matters to architects evaluating whether to
adopt the full pattern or simply enforce better testing discipline.

The additions beyond TDD:

- **Explicit lifecycle:** the *specify → generate → operate → measure → regenerate* cycle is a
  first-class concern, not a developer practice.
- **Dual-score measurement:** entropy score (implementation decay) and artifact drift score (spec
  consistency) together provide a regeneration gate that test coverage alone does not.
- **Structured artifact layer:** `intent.md`, regeneration recipe, and `system.yaml` preserve the
  knowledge needed to recreate the implementation — not just verify it.
- **Regeneration as the exit:** TDD enables confident refactoring; RA enables confident discarding.

**Still open:** Whether the overhead of the full artifact layer is justified in domains where strong
TDD is already practiced, or whether a lighter adoption (Levels 1–3 in the maturity model) captures
most of the value.
