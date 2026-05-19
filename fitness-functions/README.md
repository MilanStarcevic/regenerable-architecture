# Implementation Entropy Fitness Functions

Fitness functions are automated checks that measure implementation health in a capability capsule.
They answer one question: has accumulated implementation entropy — complexity, duplication, semantic drift, weak tests
— crossed the threshold where regeneration is safer than further refactoring?

This document defines:

1. **The interface contract** — what any fitness function implementation must produce
2. **The six entropy signals** — what to measure, why it matters, and which existing tools cover it
3. **The composite entropy score** — how signals combine into a regeneration trigger

The reference Python implementation lives in
[examples/pricing-discount-capsule/fitness/](../examples/pricing-discount-capsule/fitness/).

---

## Interface Contract

Each fitness check takes a capsule directory as input and returns a JSON-compatible dict with at
minimum a `"score"` key:

```json
{
  "score": 0.0
}
```

- `score` is a float from 0 (healthy) to 100 (high implementation entropy)
- Additional keys provide supporting detail for diagnostics
- Any tool or script that produces this shape satisfies the interface

The composite entropy score runner calls each check, combines scores using the formula below, and
outputs the aggregate result.

---

## Entropy Score Formula

```
Entropy Score =
  complexity_score
+ duplication_score
+ dependency_score
+ semantic_drift_score
+ changeability_score
- test_confidence_score
```

Normalized to 0–100. Test confidence is **subtracted**: strong tests reduce the risk that structural
decay has caused undetected behavioral drift.

| Score | Status | Action |
|---|---|---|
| 0–30 | Healthy | Maintain |
| 31–50 | Watch | Monitor trends |
| 51–70 | Warning | Refactor |
| 71–85 | High | Regenerate |
| 86–100 | Critical | Urgent regeneration |

Thresholds should be calibrated to your team and domain. Start conservative; tighten as your
baseline improves.

---

## The Six Signals

### 1. Complexity

**What to measure:** Functions too long to reason about, excessive branching, maximum nesting depth.

**Why it matters for regenerability:** AI models generate correct but over-engineered code. Over
multiple generations, complexity compounds into implementations that are difficult to verify,
modify, or reason about confidently.

**Existing tools:**

| Tool | Language |
|---|---|
| SonarQube `cognitive_complexity`, `cyclomatic_complexity` | Any |
| `radon cc` | Python |
| `flake8-cognitive-complexity` | Python |
| Roslyn analyzers, NDepend | C# |
| ESLint `complexity` rule | JavaScript / TypeScript |
| Count branches (if/for/while/try) and nesting depth | Any (custom) |

---

### 2. Duplication

**What to measure:** Repeated lines and duplicate code blocks across the capsule.

**Why it matters for regenerability:** AI models generate the same solution in multiple places
without recognising the overlap. When a business rule changes, one copy gets updated and the other
does not. Neither is authoritative.

**Existing tools:**

| Tool | Language |
|---|---|
| SonarQube `duplicated_lines_density` | Any |
| `jscpd` (JavaScript Copy/Paste Detector) | Many |
| `pylint` similarity checker | Python |
| N-gram block matching on normalised source lines | Any (custom) |

---

### 3. Dependency Accumulation

**What to measure:** Total import count, external dependency count, presence of unexpectedly
heavyweight dependencies.

**Why it matters for regenerability:** AI models import libraries freely, often for single-use
convenience. Dependency accumulation is difficult to reverse cleanly and increases the surface area
of each regeneration.

**Existing tools:**

| Tool | Language |
|---|---|
| `depcheck` | JavaScript / TypeScript |
| `npm audit` / `yarn audit` | JavaScript / TypeScript |
| NuGet dependency analysis | C# |
| `pipdeptree` | Python |
| Parse package manifests (`package.json`, `*.csproj`, `requirements.txt`, `go.mod`) | Any |
| Count import statements by type (stdlib vs external) | Any (custom) |

---

### 4. Semantic Drift

**What to measure:** Alignment between the implementation vocabulary and the business domain
declared in `intent.md`.

**Why it matters for regenerability:** Domain terms get renamed across generations — "discount
percentage" becomes "rate multiplier," "customer tier" becomes "loyalty level." The code still
produces correct results but no longer maps back to the specification. Future regeneration amplifies
the drift.

**Existing tools:**

| Tool | Language |
|---|---|
| SonarQube | Does not cover semantic alignment |
| LLM-assisted review comparing `intent.md` to implementation | Any |
| Spec-to-test traceability matrices | Any |
| Production behavior comparison against golden masters | Any |
| Term presence check: domain vocabulary from `intent.md` appears in source files | Any (heuristic) |

Semantic drift is the signal most likely to require a custom check or LLM-assisted review regardless
of tooling. Heuristic term matching catches obvious drift; it misses subtle reinterpretation of
business rules.

---

### 5. Test Confidence

**What to measure:** Test count, presence of behavioral acceptance tests, presence of invariant
tests, whether the suite currently passes.

**Why it matters for regenerability:** This score is **subtracted** from the composite total. High
confidence means regeneration is safer — the behavioral specification is strong enough to catch
divergence. Low confidence means regeneration is risky regardless of implementation quality.

**Existing tools:**

| Tool | Language |
|---|---|
| SonarQube `coverage`, `test_failures`, `test_success_density` | Any |
| `pytest-cov` | Python |
| `dotnet test --collect:"XPlat Code Coverage"` | C# |
| Jest `--coverage`, `c8` | JavaScript / TypeScript |
| Count test files by naming convention; run suite and check exit code | Any (custom) |

---

### 6. Changeability

**What to measure:** Recent churn in git history, TODO/FIXME/HACK comment count.

**Why it matters for regenerability:** High churn may indicate implementation thrashing. Deferred
problems marked as TODO or HACK accumulate into regeneration triggers.

**Existing tools:**

| Tool | Language |
|---|---|
| SonarQube `code_smells`, `technical_debt` | Any |
| `git log --name-only` (language-agnostic churn) | Any |
| Grep for TODO/FIXME/HACK/XXX patterns | Any |

---

## Using SonarQube

If your team already runs SonarQube, you can derive an approximate entropy score without custom checks:

| Signal | SonarQube metric |
|---|---|
| Complexity | `cognitive_complexity` violations, normalised |
| Duplication | `duplicated_lines_density` |
| Dependency accumulation | Custom rules or manual review |
| Test confidence | `coverage` + `test_success_density`, inverted |
| Changeability | `code_smells`, normalised |
| Semantic drift | Not covered — requires custom check or LLM-assisted review |

Semantic drift is the one signal SonarQube does not address. It requires intent documents and a
mechanism to verify that implementation vocabulary still matches them.

---

## Reference Implementation

A working Python implementation of all six checks is included in the example capsule:

```
examples/pricing-discount-capsule/fitness/
├── entropy_score.py           ← composite score runner
├── complexity_check.py
├── duplication_check.py
├── dependency_check.py
├── test_confidence_check.py
├── semantic_drift_check.py
└── changeability_check.py
```

These implementations are Python-specific. They satisfy the interface contract above and are
intended as a reference when implementing checks for your own stack.

Run against the example capsule from the repository root:

```bash
python3 examples/pricing-discount-capsule/fitness/entropy_score.py
```

Or from the capsule directory:

```bash
python3 fitness/entropy_score.py
```
