# Implementation Decay Fitness Functions

Fitness functions are automated checks that measure implementation health in a capability capsule.
They answer one question: have the implementation decay signals — complexity, duplication, dependency
accumulation, test confidence, changeability — crossed the threshold where regeneration is safer than
further refactoring?

This document defines:

1. **The interface contract** — what any fitness function implementation must produce
2. **The five mechanical signals** — what to measure, why it matters, and which existing tools cover it
3. **The judgment signal** — semantic drift, evaluated separately at the pre-regeneration gate
4. **The signal dashboard** — how signals are presented and how regeneration is triggered
5. **The default regeneration policy** — how the dashboard drives the regeneration decision

The reference Python implementation lives in
[examples/pricing-discount-capsule/fitness/](../examples/pricing-discount-capsule/fitness/).

---

## Interface Contract

Each individual fitness check takes a capsule directory as input and returns a JSON-compatible dict
with at minimum a `"score"` key:

```json
{
  "score": 0.0
}
```

- `score` is a float from 0 (healthy) to 100 (high decay signal)
- Additional keys provide supporting detail for diagnostics
- Any tool or script that produces this shape satisfies the interface

The signal dashboard runner calls each check, maps each raw score to a status, and outputs a
dashboard keyed by signal name. There is no composite numeric score. See the dashboard specification
below.

---

## Signal Dashboard

The signals do not combine into a single number. Each signal has its own status; the dashboard
presents them side by side. Regeneration is triggered by a policy evaluated across the dashboard.

The signals are qualitatively different and do not share units: complexity accumulates in functions,
duplication accumulates in code blocks, dependency accumulation is a count, test confidence is an
inverted coverage measure, and changeability tracks churn and deferred markers. Summing them invited
argument about the arithmetic rather than about the thresholds. A dashboard makes asymmetric,
domain-specific calibration natural: a team may tolerate higher complexity but demand strict test
confidence; another may weight dependency growth heavily because their regeneration surface is large.

### Dashboard output shape

The dashboard runner produces a JSON object keyed by signal name. Each signal entry contains its raw
measurement, a status, and a short runtime note. There is no top-level numeric score.

```json
{
  "signals": {
    "complexity":             { "raw": 14.1,  "status": "healthy", "note": "..." },
    "duplication":            { "raw": 9.9,   "status": "healthy", "note": "..." },
    "dependency_accumulation":{ "raw": 16.7,  "status": "healthy", "note": "..." },
    "test_confidence":        { "raw": 100.0, "status": "healthy", "note": "..." },
    "changeability":          { "raw": 13.0,  "status": "healthy", "note": "..." },
    "semantic_drift":         { "raw": 4.3,   "status": "healthy", "note": "...", "kind": "judgment" }
  },
  "regeneration_indicated": false,
  "policy_reason": "all signals within acceptable thresholds"
}
```

### Status levels

Each signal uses four status levels. The levels mean different things per signal — decay looks
different depending on what is accumulating.

| Status | General meaning |
|---|---|
| `healthy` | Within expected bounds; no action required |
| `watch` | Elevated; monitor trends before the next change cycle |
| `warning` | Notably elevated; consider targeted intervention |
| `critical` | Severe; regeneration is indicated if test confidence permits |

### Default regeneration policy

**Default regeneration policy.** Regenerate when any one of the following holds: a judgment signal
is in `warning` or `critical`; two or more mechanical signals are in `warning`; any single
mechanical signal is in `critical`. This policy is a calibration starting point. Teams should expect
to adjust it after the first few regeneration cycles, based on observed false positives and false
negatives.

---

## The Five Mechanical Signals

Mechanical signals run continuously in CI. Each has its own status thresholds; they do not combine.

---

### 1. Complexity

**What to measure:** Functions too long to reason about, excessive branching, maximum nesting depth.

**Why it matters for regenerability:** AI models generate correct but over-engineered code. Over
multiple generations, complexity compounds into implementations that are difficult to verify,
modify, or reason about confidently.

**Status levels for this signal:**

| Status | Meaning |
|---|---|
| `healthy` | Function count and branching are within expected bounds; the implementation is navigable |
| `watch` | Some functions are approaching the upper bound; nesting depth is increasing |
| `warning` | Multiple overlong functions or excessive branching; the implementation is difficult to reason about confidently |
| `critical` | Structural complexity makes the implementation unreliable to modify or verify; regeneration is indicated |

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

**Status levels for this signal:**

| Status | Meaning |
|---|---|
| `healthy` | No significant code repetition detected |
| `watch` | Minor repetition present; unlikely to affect regeneration safety yet |
| `warning` | Repeated logic blocks found; business rules may have diverged between copies |
| `critical` | Severe duplication; a rule change will likely be applied inconsistently across copies |

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

**Status levels for this signal:**

| Status | Meaning |
|---|---|
| `healthy` | Imports are minimal and deliberate; no discouraged libraries present |
| `watch` | Dependency count is growing; worth reviewing whether each import is intentional |
| `warning` | External dependency count is elevated; regeneration surface is wider than intended |
| `critical` | Discouraged libraries present or dependency count is high enough to risk unintended regeneration behavior |

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

### 4. Test Confidence

**What to measure:** Test count, presence of behavioral acceptance tests, presence of invariant
tests, whether the suite currently passes.

**Why it matters for regenerability:** High test confidence means regeneration is safer — the
behavioral specification is strong enough to catch divergence. Low test confidence means
regeneration is risky regardless of implementation quality; a regenerated implementation may pass
weak tests while diverging from business behavior.

**Status levels for this signal:**

| Status | Meaning |
|---|---|
| `healthy` | Comprehensive behavioral test coverage; regeneration is safe from a test standpoint |
| `watch` | Test coverage is adequate but not thorough; behavioral gaps may exist |
| `warning` | Test coverage is thin; regeneration risks introducing undetected behavioral regressions |
| `critical` | Tests are insufficient to verify a regenerated implementation; do not regenerate until coverage is strengthened |

**Existing tools:**

| Tool | Language |
|---|---|
| SonarQube `coverage`, `test_failures`, `test_success_density` | Any |
| `pytest-cov` | Python |
| `dotnet test --collect:"XPlat Code Coverage"` | C# |
| Jest `--coverage`, `c8` | JavaScript / TypeScript |
| Count test files by naming convention; run suite and check exit code | Any (custom) |

---

### 5. Changeability

**What to measure:** Recent churn in git history, TODO/FIXME/HACK comment count.

**Why it matters for regenerability:** High churn may indicate implementation thrashing. Deferred
problems marked as TODO or HACK accumulate and signal that the implementation is being patched
rather than understood.

**Status levels for this signal:**

| Status | Meaning |
|---|---|
| `healthy` | No deferred problem markers; low recent churn; the implementation is stable |
| `watch` | Minor churn or a small number of deferred markers; worth monitoring |
| `warning` | High churn or significant deferred markers suggest the implementation is unstable |
| `critical` | The implementation is thrashing; churn patterns indicate instability that targeted editing cannot resolve |

**Existing tools:**

| Tool | Language |
|---|---|
| SonarQube `code_smells`, `technical_debt` | Any |
| `git log --name-only` (language-agnostic churn) | Any |
| Grep for TODO/FIXME/HACK/XXX patterns | Any |

---

## The Judgment Signal

### Semantic Drift

Semantic drift is evaluated separately from the mechanical signals. It is not a continuous CI check;
it runs at the pre-regeneration gate, when regeneration is being considered. Mechanical signals can
be computed automatically; semantic drift — whether the implementation has behaviorally diverged from
the declared intent — requires either LLM-assisted review or careful manual evaluation. Running it
on every commit would be expensive and would return false positives as the implementation evolves
normally between intents.

**What to measure:** Whether the implementation has behaviorally diverged from the business intent
declared in `intent.md`. Drift is behavioral: the code produces different outcomes than the intent
specifies. Drift is not: different naming, different internal structure, additional logging,
performance choices, or any implementation decision the intent does not constrain.

**Why it matters for regenerability:** Behavioral drift that passes tests will be amplified by
regeneration. If the implementation has silently diverged from intent, the next regeneration will
reproduce the drift — or introduce a different divergence — because the intent document is the
ground truth the recipe reads from.

**Status levels for this signal:**

| Status | Meaning |
|---|---|
| `healthy` | No behavioral divergence detected between implementation and `intent.md` |
| `watch` | Minor vocabulary or structural drift noted; review before regenerating |
| `warning` | Behavioral divergence likely; intent-implementation gap should be resolved before regenerating |
| `critical` | Significant behavioral divergence detected; regeneration guided by current `intent.md` will not reproduce current behavior |

**Evaluation approaches:**

| Approach | Language |
|---|---|
| LLM-assisted review comparing `intent.md` to implementation (see `fitness-functions/prompts/semantic-drift.md`) | Any |
| Spec-to-test traceability matrices | Any |
| Production behavior comparison against golden masters | Any |
| Term presence check: domain vocabulary from `intent.md` appears in source (heuristic only) | Any |

The heuristic term-presence check in the reference implementation catches obvious vocabulary drift
but misses subtle behavioral reinterpretation. See Task 2 of the implementation notes for the
LLM-judged version.

---

## Using SonarQube

If your team already runs SonarQube, you can populate the mechanical signal statuses without custom
checks:

| Signal | SonarQube metric |
|---|---|
| Complexity | `cognitive_complexity` violations, normalised |
| Duplication | `duplicated_lines_density` |
| Dependency accumulation | Custom rules or manual review |
| Test confidence | `coverage` + `test_success_density` |
| Changeability | `code_smells`, normalised |
| Semantic drift | Not covered — requires LLM-assisted review |

Semantic drift is the one signal SonarQube does not address. It requires intent documents and an
LLM-assisted check to determine whether the implementation has behaviorally diverged from them.

---

## Reference Implementation

A working Python implementation of all five mechanical checks and the heuristic semantic drift check
is included in the example capsule:

```
examples/pricing-discount-capsule/fitness/
├── decay_dashboard.py       ← signal dashboard runner
├── complexity_check.py
├── duplication_check.py
├── dependency_check.py
├── test_confidence_check.py
├── semantic_drift_check.py    ← heuristic; see prompts/semantic-drift.md for LLM version
└── changeability_check.py
```

These implementations are Python-specific. They satisfy the interface contract above and are
intended as a reference when implementing checks for your own stack.

Run against the example capsule from the repository root:

```bash
python3 examples/pricing-discount-capsule/fitness/decay_dashboard.py
```

Or from the capsule directory:

```bash
python3 fitness/decay_dashboard.py
```
