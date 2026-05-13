# Open Questions

These questions do not have settled answers. They are worth working through before applying the pattern at scale, because the decisions made here determine whether the lifecycle actually functions in practice or just looks good on paper.

---

## 1. How do you detect semantic drift reliably?

The heuristic approaches in this repository—checking for domain terms in tests, verifying invariants exist—are approximations. They can miss drift and produce false positives.

More robust approaches might include:
- LLM-assisted review: ask an AI model whether the implementation matches the intent document, with human approval gates
- Formal specification languages that can be checked against implementation
- Production behavior comparison: does the system's actual behavior match what the intent document predicts?
- Traceability matrices: each requirement in `intent.md` mapped to specific tests

How much semantic drift is acceptable before triggering regeneration versus a specification review?

---

## 2. What is the right granularity for a capability capsule?

Too fine: nano-service explosion. Too coarse: monolithic capsules that are never actually regenerated because they are too large.

There is no universal answer. Possible heuristics:
- A capsule should be regenerable in a single AI session
- A capsule should have fewer than N acceptance tests (rough size signal)
- A capsule should map to a single business capability, not a technical function
- A capsule should be owned by a single team

How do you decide when a growing capsule should be split?

---

## 3. How do fitness function thresholds evolve as systems mature?

Initial thresholds are calibrated against a naive baseline. As the team gets better at writing regenerable capsules, the baseline shifts. Should thresholds tighten over time? Should they be set relative to a team's historical performance rather than absolute values?

A team that consistently achieves a slop score of 10 should probably recalibrate their threshold from 50 to 25—otherwise the fitness function loses its signal.

---

## 4. How do you govern regeneration in teams with many contributors?

Regeneration is a high-stakes operation. The implementation is discarded. If the durable artifacts are not strong enough, the regenerated implementation may be wrong.

Questions:
- Who can authorize a regeneration?
- What review process should precede regeneration?
- How do you ensure the regeneration recipe is current before triggering?
- What happens if regeneration fails mid-process in a production system?

---

## 5. When does a disposable capsule earn the right to become a durable domain?

Some capsules start as experiments and become critical. At some point, the data they generate, the contracts they establish, or the integrations they support become too valuable to treat as disposable.

How do you recognize this transition? What process should trigger an ownership review? How do you migrate a capsule from disposable to durable without disruption?

---

## 6. How do you handle capsule-to-capsule contracts?

When capsules call each other, the calling capsule depends on the callee's contract. If the callee is regenerated, its contract may change.

- Should capsule-to-capsule contracts be treated as consumer-driven contracts?
- How do you version internal contracts between capsules of the same system?
- If both capsules are regenerated simultaneously, how do you ensure contract compatibility?

---

## 7. What is the role of the regeneration recipe in a team that uses multiple AI tools?

The regeneration recipe documents how to recreate the implementation. But AI tools differ in their capabilities and tendencies. A recipe that works well with one model may produce poor results with another.

- Should recipes be tool-agnostic?
- Should recipes capture model-specific guidance as optional annotations?
- How do you evaluate whether a recipe is "good enough" before it is needed?

---

## 8. How do you measure the value of durable artifacts over time?

The durable artifact investment—writing intent documents, tests, contracts, regeneration recipes—is upfront cost that pays off at regeneration time. But regeneration may be infrequent. How do you justify the investment?

Possible metrics:
- Time to regenerate: how long does regeneration take with good versus poor durable artifacts?
- Regeneration success rate: how often does the first regeneration pass all tests?
- Onboarding time: how long does a new team member take to understand a capsule?
- Change safety: how often do changes cause unexpected breakage?

---

## 9. Is there a meaningful boundary between regenerable architecture and test-driven development?

Strong behavioral tests are a prerequisite for safe regeneration. In some sense, a well-tested capsule with clear contracts is already close to regenerable.

What does regenerable architecture add beyond rigorous TDD? Is the regeneration recipe the key addition? Is the slop measurement? Is it the explicit lifecycle?

---

## 10. How does regenerable architecture interact with long-running processes and stateful systems?

The pricing discount capsule in this repository is stateless. Regeneration is straightforward.

For capsules that manage long-running workflows, stateful machines, or saga-style coordination, regeneration becomes harder:
- In-flight workflows may need to complete before regeneration
- State migration may be required
- The regeneration recipe must account for state transition edge cases

How do you design regenerable stateful capsules?
