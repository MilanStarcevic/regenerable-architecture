# AI Slop: Definition and Detection

## What Is AI Slop?

AI slop is the gradual accumulation of implementation quality debt in AI-generated or AI-assisted code. It is not a single bug or a single bad decision. It is the compound effect of many small, individually defensible choices that together erode the trust, clarity, and maintainability of a system.

The term "slop" is deliberately unglamorous. It is not "technical debt" (too neutral), not "code smell" (too narrow), and not "AI hallucination" (a different problem). Slop is what happens when generated code is accepted without architectural discipline.

## How Slop Accumulates

### Pattern 1: Complexity Without Purpose

AI models generate code that is correct but over-engineered. A five-line function becomes a twenty-line function with intermediate variables, error branches for impossible inputs, and abstraction layers that exist because the model "completed the pattern" from training data.

Over many generations and edits, this compounds.

### Pattern 2: Semantic Drift

The implementation drifts away from the business vocabulary. Domain terms are renamed for code convenience. A "discount percentage" becomes a "rate multiplier." A "customer tier" becomes a "loyalty level." The code still works, but the next engineer reading it cannot map it back to the business specification without detective work.

### Pattern 3: Dependency Accumulation

AI models pull in dependencies freely. A single convenience function introduces a library. Over time, the capsule accumulates imports it barely uses, with dependency chains that were not reviewed or intentional.

### Pattern 4: Duplicated Logic

Similar logic appears in multiple places—sometimes identically, sometimes in slightly different forms. The AI generated it twice in slightly different contexts. Both instances pass tests. Neither is authoritative.

### Pattern 5: Test Drift

Tests are added to verify implementation behavior rather than business behavior. They test that a private helper returns a specific intermediate value, or that an internal retry mechanism triggers under specific conditions. When the implementation is regenerated, these tests break—not because the business behavior changed, but because the implementation changed.

### Pattern 6: Invented Behavior

AI models sometimes add behavior that was not requested. Extra validation, additional fallback logic, unsolicited error handling. The behavior may be harmless or it may mask a real problem. Either way, it was not specified and is not tested against the business requirement.

## Measuring Slop

Slop is measurable through a combination of static analysis, test quality signals, and semantic checks.

### Complexity Score

Measures structural complexity of the implementation:

- Function length in lines
- File length in lines
- Cyclomatic complexity (branch count)
- Nesting depth

High complexity is not always slop. Complex business logic may require complex code. But AI-generated complexity often exceeds what the problem requires.

### Duplication Score

Measures repeated patterns in the implementation:

- Identical non-trivial lines
- Near-duplicate blocks
- Repeated structural patterns

Duplication in AI-generated code is a strong signal of slop: the model generated the same solution twice without recognizing it.

### Dependency Score

Measures dependency health:

- Total import count
- External (non-standard-library) import count
- Presence of forbidden or unexpected dependencies
- Dependency growth trend

### Semantic Drift Score

Measures the alignment between implementation and intent:

- Domain terms from `intent.md` present in implementation and tests
- Critical invariants (e.g., maximum discount) expressed in tests
- Business behavior (e.g., explanation generation) explicitly tested
- Contract terms reflected in implementation vocabulary

Real semantic drift detection at scale requires stronger methods:

- Spec-to-test traceability matrices
- Requirements coverage metrics
- Formal invariant specifications
- LLM-assisted review with human approval gates
- Production behavior comparison against golden masters

The fitness functions in this repository use heuristic approximations suitable for demonstration.

### Test Confidence Score

Measures the quality of the test suite as a guide for safe regeneration:

- Total test count
- Presence of acceptance tests (end-to-end behavioral tests against the public API)
- Presence of invariant or property-based tests
- Test pass status

Test confidence is subtracted from the slop score: high test confidence reduces slop risk.

### Changeability Score

Measures implementation stability and change history:

- Churn in recent git commits
- TODO/FIXME/HACK comment count
- Unstable file count

High churn may indicate either healthy evolution or thrashing. Context determines the interpretation.

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

The thresholds are configurable. A team with strong test coverage and clear contracts may tolerate higher complexity scores. A team in a regulated domain may set lower thresholds across all dimensions.

## What Slop Is Not

- **A bug**: Slop can exist in code with no bugs.
- **A style violation**: Slop is not about formatting or naming conventions.
- **A performance problem**: Slop can exist in fast code.
- **Intentional complexity**: Well-documented complexity serving a genuine purpose is not slop.
- **All AI-generated code**: Many AI-generated implementations are clean and well-structured.

Slop is specifically the accumulated quality decay that makes a system harder to trust, understand, and regenerate safely.
