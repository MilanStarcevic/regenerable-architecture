# Regenerable Architecture — Architect Cheat Sheet

## Use this pattern when

- Implementation is cheap to recreate (AI-assisted generation is available)
- Durable behavior is expensive to rediscover (domain knowledge is concentrated in key people)
- AI-generated code is the primary implementation source
- Capability boundaries are stable enough to commit to in a contract
- Behavioral tests are strong, or the team has the discipline to write them

## Do not use this pattern when

- The domain is exploratory and intent cannot yet be committed to
- Tests are weak and the team will not maintain them
- The implementation is itself the specification (standards-conformant code, protocol implementations)
- The system is short-lived and the investment will not be recovered
- No one will maintain the durable artifacts as the domain evolves

See [when-not-to-use.md](when-not-to-use.md) for detailed contraindications.

---

## The two measures

| Measure | Meaning | Bad state means |
| --- | --- | --- |
| **Signal dashboard** | How decayed is the implementation? (5 mechanical signals + 1 judgment signal) | Regeneration is indicated |
| **Artifact drift score** | How unsafe are the regeneration inputs? | Regeneration is blocked |

Both must be checked before regenerating. Dashboard indicates regeneration, artifact drift is low:
regenerate. Artifact drift is high: strengthen artifacts first regardless of dashboard status.

---

## The lifecycle

```
Specify → Generate → Operate → Measure Decay Signals → Regenerate
```

| Phase | Primary artifact | Question |
| --- | --- | --- |
| Specify | `intent.md`, contracts, tests, recipe | Is the durable layer complete and consistent? |
| Generate | `src/` (disposable) | Does the generated implementation pass all behavioral tests? |
| Operate | Runtime metrics, SLOs | Is the system healthy? |
| Measure | Signal dashboard, artifact drift score | Is the implementation decaying? Are the artifacts drifting? |
| Regenerate | New `src/` from durable artifacts | Did the regeneration pass all tests? |

---

## The durable layer (preserve these)

| Artifact | What it captures |
| --- | --- |
| `intent.md` | Why the capsule exists; what it must never get wrong |
| `ports/inbound/openapi.yaml` | The public API commitment to callers |
| `ports/outbound/dependencies.yaml` | What this capsule consumes; stub behaviors for testing |
| `tests/test_acceptance.py` | Behavioral proof against contract and intent |
| `tests/test_invariants.py` | Rules that must hold for all inputs |
| `tests/test_contract.py` | Contract conformance |
| `tests/test_integration.py` | Outbound adapter against the real dependency |
| `regeneration-recipe.md` | Step-by-step instructions to recreate the implementation |
| `system.yaml` (root) | Dependency graph across all capsules |

---

## The disposable layer (safe to discard)

- `src/` — generated implementation
- Framework glue and adapters
- Local optimizations

---

## Before proposing a capsule boundary

Use [capsule-assessment-checklist.md](capsule-assessment-checklist.md). Key questions:

1. Can you write a single-paragraph `intent.md` that a domain expert would agree with?
2. Can the inbound contract be defined before implementation?
3. Are outbound dependencies known and explicit?
4. Is data classified — canonical data is not owned by the disposable implementation?
5. Could a competent engineer regenerate this from the artifacts alone?

---

## Before regenerating

Use [regeneration-readiness-checklist.md](regeneration-readiness-checklist.md). The hard gates:

- `intent.md` is current
- Acceptance tests are behavioral and pass
- Regeneration recipe references files that exist
- Artifact drift score is below the block threshold (score < 16)
- Downstream consumers are identified and notified

---

## Adoption stages

| Level | What the team has | What it enables |
| --- | --- | --- |
| 0 | Nothing | Fast generation, invisible decay |
| 1 | `intent.md` maintained | Context for regeneration |
| 2 | Contracts defined before implementation | Safe callers |
| 3 | Behavioral tests written from intent | Verifiable regeneration |
| 4 | Recipe + fitness functions + readiness checklist | Intentional, safe regeneration |
| 5 | Routine regeneration on threshold triggers | Graceful degradation as a system property |

See [adoption-maturity-model.md](adoption-maturity-model.md) for diagnostic questions per level.
