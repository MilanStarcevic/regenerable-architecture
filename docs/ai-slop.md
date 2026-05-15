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

Slop is measurable through six signals: complexity, duplication, dependency accumulation, semantic drift, test confidence, and changeability. Test confidence is subtracted from the composite total — strong tests mean regeneration is safer regardless of structural decay. See [fitness-functions/README.md](../fitness-functions/README.md) for the formula, thresholds, and tool alternatives for each signal.

---

## What Slop Is Not

- **A bug.** Slop can exist in code with no observable bugs.
- **A style violation.** Slop is not about formatting or naming conventions.
- **A performance problem.** Slop can exist in fast code.
- **Intentional complexity.** Well-documented complexity serving a genuine purpose is not slop.
- **All AI-generated code.** Many AI-generated implementations are clean and appropriate. Slop is a decay pattern, not an inherent property of generation.

Slop is specifically the accumulated implementation decay that makes a system harder to understand, trust, and regenerate safely.
