# AI Slop: Definition and Detection

## What Is AI Slop?

AI slop is the gradual accumulation of implementation quality decay in AI-generated or AI-assisted code. It is not a single bug or a single bad decision. It is the compound effect of many small, individually defensible choices that together erode the trust, clarity, and maintainability of a system.

The term "slop" is deliberately unglamorous. It is not "technical debt" (too neutral), not "code smell" (too narrow), and not "AI hallucination" (a different problem). Slop is what happens when generated code is accepted and evolved without architectural discipline: the right tests in the wrong places, the right behavior under the wrong name, the right logic duplicated across the wrong contexts.

---

## How Slop Accumulates

### Pattern 1: Complexity Without Purpose

AI models generate code that is correct but over-engineered for the problem. A five-line function becomes twenty lines with intermediate variables, error branches for inputs the business never sends, and abstraction layers that exist because the model completed a structural pattern from training data rather than reasoning about the actual requirement.

Over multiple generations and edits, this compounds.

### Pattern 2: Semantic Drift

The implementation vocabulary drifts away from the business domain. Domain terms are renamed for code style or convenience: "discount percentage" becomes "rate multiplier," "customer tier" becomes "loyalty level," "active campaign" becomes "promotion flag." The code still produces correct results, but the next engineer reading it cannot map it back to the business specification without detective work. The intent document says one thing; the implementation says another.

### Pattern 3: Dependency Accumulation

AI models import dependencies freely. A single convenience function introduces a library. The next generation adds another. Over time, the capsule accumulates imports it barely uses, with transitive dependency chains that were never reviewed or intentional. Dependency accumulation is difficult to reverse cleanly.

### Pattern 4: Duplicated Logic

Similar logic appears in multiple places—sometimes identically, sometimes in slightly different forms. The model generated the same solution in two contexts without recognizing the overlap. Both instances pass tests. Neither is authoritative when a business rule changes. The engineer changing the rule may not find both copies.

### Pattern 5: Test Drift

Tests are added that verify implementation internals rather than business behavior: that a private helper returns a specific intermediate value, that an internal cache is populated in a particular order, that a specific exception type is raised for an input the business never actually sends. These tests do not provide evidence that the business behavior is correct. They verify what the AI built, not what the business needs. When the implementation is regenerated with a different internal structure, they fail—but for the wrong reasons, producing noise that makes it harder to distinguish genuine behavioral regressions from structural changes.

### Pattern 6: Invented Behavior

AI models sometimes add behavior that was not requested: extra validation at the wrong layer, defensive fallbacks that mask real errors, retry logic that hides latency problems. The behavior may be harmless, or it may silently change the system's semantics. Either way, it was not specified, is not tested against the business requirement, and may survive into regenerations as a misread "intended feature."

---

## Measuring Slop

Slop is measurable through a combination of static analysis, test quality signals, and semantic checks.

### Complexity Score

Measures the structural complexity of the implementation:

- Function length in lines
- File length in lines
- Branch count (if/elif/else/for/while/try/except)
- Maximum nesting depth

High complexity is not always slop—some business logic is genuinely complex. But AI-generated complexity frequently exceeds what the problem requires.

### Duplication Score

Measures repeated patterns in the implementation:

- Identical non-trivial lines appearing more than once
- Repeated blocks of N or more consecutive lines
- Near-identical structural patterns

Duplication in AI-generated code is a strong slop signal: the model generated the same solution in two contexts without recognizing the overlap.

### Dependency Score

Measures dependency health:

- Total import count
- External (non-standard-library) import count
- Presence of discouraged or unexpected dependencies
- Average imports per file

### Semantic Drift Score

Measures alignment between the implementation and the business intent declared in `intent.md`:

- Domain terms from `intent.md` present in implementation and test files
- Critical invariants expressed in tests (e.g., maximum discount cap, non-negative output)
- Business behavior explicitly tested (e.g., explanation generation, not just output value)

Real semantic drift detection at scale requires stronger methods than heuristic term matching:

- Spec-to-test traceability: each requirement mapped to specific tests
- Formal invariant specifications that can be checked mechanically
- LLM-assisted review comparing intent documents to implementation behavior, with human approval gates
- Production behavior comparison against golden masters from before the drift occurred

The fitness functions in this repository use heuristic approximations that are sufficient for demonstration and for catching obvious drift.

### Test Confidence Score

Measures the quality of the test suite as a guide for safe regeneration:

- Total test count
- Presence of acceptance tests (behavioral tests against the public API)
- Presence of invariant or property-based tests
- Whether the test suite currently passes

Test confidence is **subtracted** from the slop score. High confidence means regeneration is safer; low confidence means regeneration is risky regardless of implementation quality.

### Changeability Score

Measures implementation stability:

- Churn in recent git history (files changed frequently)
- TODO / FIXME / HACK comment count

High churn may reflect either healthy evolution or implementation thrashing. The score is an input to judgment, not a definitive signal.

---

## The Slop Score

```
Slop Score =
  complexity_score
+ duplication_score
+ dependency_score
+ semantic_drift_score
+ changeability_score
- test_confidence_score
```

Normalized to 0–100.

| Score | Status | Recommended Action |
|---|---|---|
| 0–30 | Healthy | Maintain |
| 31–50 | Watch | Monitor trends |
| 51–70 | Warning | Refactor |
| 71–85 | High | Regenerate |
| 86–100 | Critical | Urgent regeneration |

Thresholds should be calibrated to the team and domain. A team with consistently strong tests may tolerate higher complexity; a regulated-domain team may set tighter thresholds on semantic drift.

---

## What Slop Is Not

- **A bug.** Slop can exist in code with no observable bugs.
- **A style violation.** Slop is not about formatting or naming conventions.
- **A performance problem.** Slop can exist in fast code.
- **Intentional complexity.** Well-documented complexity serving a genuine purpose is not slop.
- **All AI-generated code.** Many AI-generated implementations are clean and appropriate. Slop is a decay pattern, not an inherent property of generation.

Slop is specifically the accumulated implementation decay that makes a system harder to understand, trust, and regenerate safely.
