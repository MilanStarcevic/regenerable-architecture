# Adoption Maturity Model

Regenerable Architecture can be adopted incrementally. The team does not have to start at full
lifecycle discipline. This model describes the stages teams move through, what each stage requires,
what it enables, and what the meaningful advancement looks like.

The model is descriptive, not prescriptive. Teams do not need to advance in strict order — but
skipping a stage without understanding its prerequisites will undermine the stages that depend on
it.

---

## Level 0 — Unstructured Generation

**What it looks like:** Teams use AI coding tools to generate implementation code. There is no
consistent discipline around specification, testing, or measurement. Generated code accumulates
alongside hand-written code. Quality varies by author and day.

**What it lacks:** Any durable artifact that would survive the implementation being discarded. If
the code were deleted, the team would need to re-examine the codebase to reconstruct intent and
contracts.

**What it enables:** Fast initial generation.

**Risk:** AI implementation entropy accumulates invisibly. There is no mechanism to detect decay, and no safe path to
regeneration.

---

## Level 1 — Intent Documentation

**What the team has added:** Before generating, engineers write an `intent.md` that captures the
business purpose, constraints, and what the capsule must never get wrong. The intent document is
maintained when the domain changes.

**What it enables:** Future engineers (and AI tools) can read the intent document to understand the
capsule without reverse-engineering the implementation. The document becomes the anchor for future
regeneration.

**What it lacks:** Contracts and behavioral tests. Intent documentation alone does not provide a
verification mechanism.

**Diagnostic question:** *If you deleted the implementation today, could you regenerate it from the
intent document alone?* At Level 1, the answer is probably not confidently — you would need to
re-examine the code to recover the contract and behavior.

---

## Level 2 — Contract-First Specification

**What the team has added:** Inbound contracts (`ports/inbound/`) are defined before implementation.
Outbound dependencies (`ports/outbound/`) are declared explicitly. Contract tests verify
conformance. Changes to public API surface are treated as versioned, breaking changes.

**What it enables:** Callers depend on a declared contract, not on observed behavior. The
implementation can change (or be regenerated) without surprising callers, as long as the contract is
preserved.

**What it lacks:** Behavioral tests strong enough to verify correctness of a regenerated
implementation. The contract describes structure; tests describe behavior.

**Diagnostic question:** *If you regenerated the implementation and it satisfied the contract but
had a subtle behavioral difference, would your tests catch it?* At Level 2, the answer is probably
not reliably.

---

## Level 3 — Behavioral Test Coverage

**What the team has added:** Acceptance tests are written against business behavior (not
implementation internals). Invariant tests cover the rules that must hold for all inputs. Tests are
written from the intent document and the contract — not from the implementation. All tests pass
before any implementation change is considered correct.

**What it enables:** Regeneration is now *verifiable*. If a new implementation passes all behavioral
tests, the team has evidence — not certainty, but evidence — that the regenerated capsule is
correct.

**What it lacks:** A measurement mechanism for knowing *when* regeneration is warranted, and a
recipe for executing it correctly.

**Diagnostic question:** *If you discarded the implementation and regenerated it from the durable
artifacts, would you trust the result?* At Level 3, the answer depends on having a recipe. Without a
recipe, generation is a prompt-and-hope exercise.

---

## Level 4 — Regeneration-Ready

**What the team has added:** A `regeneration-recipe.md` that provides step-by-step instructions for
recreating the implementation from the durable artifacts. Fitness functions are in place and run
regularly. The regeneration readiness checklist has been completed for each capsule. Durable health
fitness runs as a pre-regeneration gate.

**What it enables:** The team can regenerate a capsule intentionally, safely, and verifiably. The
cycle — specify, generate, operate, measure, regenerate — is now executable end to end.

**What it lacks:** A process for deciding *when* to regenerate, and operational experience with
regeneration as a routine event rather than an emergency measure.

**Diagnostic question:** *Have you regenerated a capsule recently?* At Level 4, the answer might be
"we could, but we haven't needed to yet." The infrastructure is in place; the practice is not yet
routine.

---

## Level 5 — Active Regeneration Lifecycle

**What the team has added:** Regeneration is a routine event, not an emergency. Slop score
thresholds trigger regeneration reviews. The team has regenerated capsules and observed that the
results are correct. Durable health fitness is part of the CI pipeline. The adoption maturity model
is not a goal — it is a reference for onboarding.

**What it enables:** The system degrades gracefully. Implementation quality does not compound
indefinitely because there is a safe exit: discard and recreate. The team can adopt new AI tools or
new generation approaches by updating the recipe, not by migrating the codebase.

**What it looks like in practice:**
- Slop scores above the warning threshold trigger a regeneration review in the team's normal cadence
- Regeneration readiness checklist is completed as part of any planned regeneration
- Capsule assessment checklist is used when proposing new capsule boundaries
- Durable artifacts are updated in the same change set as behavioral changes
- New team members are onboarded to the durable artifact structure before they touch implementation

---

## Advancement Signals

| Advancement | Signal That the Team Is Ready |
|---|---|
| 0 → 1 | The team can write `intent.md` for an existing capsule without consulting the code |
| 1 → 2 | The team can define the inbound contract before writing the implementation |
| 2 → 3 | The team writes acceptance tests from the contract and intent before generating |
| 3 → 4 | The team completes the regeneration readiness checklist and regenerates a non-critical capsule |
| 4 → 5 | The team regenerates a production capsule and verifies the result passes behavioral tests |

---

## Common Failure Modes by Stage

| Stage | Common Failure Mode |
|---|---|
| Level 1 | Intent documents written once, never updated — see [Durable Artifact Neglect](anti-patterns.md) |
| Level 2 | Contracts defined after implementation, reverse-engineered from code |
| Level 3 | Tests written against implementation internals, break on regeneration |
| Level 4 | Fitness functions measure slop but thresholds are never acted on — see [Fitness Function Theater](anti-patterns.md) |
| Level 5 | Regeneration readiness not verified before regenerating — see [Regeneration Without Tests](anti-patterns.md) |

---

## A Note on Non-Linearity

Teams often reach Level 3 in some capsules and Level 0 in others. That is normal. The maturity model
applies at the capsule level, not the system level. A team may choose to apply full lifecycle
discipline only to the capsules where AI implementation entropy is most likely to accumulate or where the cost of
behavioral regression is highest.

The pattern does not require uniform adoption. It requires that wherever it is applied, the
prerequisites for the claimed safety properties are actually in place.
