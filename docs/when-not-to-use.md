# When Not to Use Regenerable Architecture

Regenerable Architecture imposes real overhead: durable artifacts must be maintained with the same
rigor as code, fitness functions must be run and acted on, and every regeneration requires a test
suite strong enough to verify correctness. That overhead is justified when it solves a real problem.
It is waste when it does not.

---

## Contraindications

### Exploratory or proof-of-concept work

When the goal is to discover whether something is worth building, the intent is unknowable upfront.
Writing a trustworthy `intent.md` requires understanding the problem well enough to commit to what
the capsule must never get wrong. Early exploration does not yet have that understanding.

Apply this pattern after the problem is understood, not while discovering it.

---

### Solo projects and very small teams without test discipline

Regenerable Architecture derives its safety guarantee from behavioral tests. If a team will not
maintain strong, behavior-first test suites, then "regeneration" is just rewriting — with the added
risk that the lost context is unrecoverable.

The question is not whether the team is small. It is whether the team has the discipline to maintain
the durable artifacts. A small, disciplined team can apply the pattern. A large team that treats
tests as optional cannot.

---

### Throw-away code and short-lived systems

If a system is known to have a finite, short lifespan, the regeneration lifecycle has no opportunity
to pay back the investment in durable artifacts. Build it, ship it, retire it.

---

### Domains where the implementation is the specification

Some systems implement a published standard (a protocol, a file format, a regulatory schema) where
the specification is external and authoritative. The implementation's job is to match the standard
exactly. There is no "intent" that the team controls; the intent is the standard itself. The
regeneration lifecycle does not apply in this mode.

---

### Highly regulated domains without established formal-verification tooling

Regenerable Architecture's safety depends on behavioral tests, not formal proofs. In domains where
correctness must be certified to a regulatory standard (certain medical device software, avionics,
safety-critical control systems), the test-based verification model may not meet the required
assurance level. This is not a reason to avoid the pattern — it is a reason to supplement it with
the domain's required verification methods before treating regeneration as safe.

---

### Systems with no stable business capability boundary

The capsule boundary requires a stable unit of business capability. If the domain model is changing
so rapidly that even the capability structure is renegotiated frequently, the capsule boundaries
will require constant restructuring. The overhead of maintaining durable artifacts for unstable
boundaries exceeds the value.

Wait until the domain model stabilizes before applying capsule structure.

---

### Teams that will not run fitness functions with real thresholds

Measuring implementation entropy and never acting on it is fitness function theater (see
[anti-patterns.md](anti-patterns.md)). If the organizational context does not support treating a
high entropy score as a genuine trigger for regeneration, the measurement layer is overhead without
benefit. In that context, invest in ordinary code quality practices instead.

