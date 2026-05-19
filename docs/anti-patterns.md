# Anti-Patterns in Regenerable Architecture

Each of these patterns represents a way that the lifecycle breaks down: either the durable artifacts
are not actually durable, the disposable layer is not actually safe to replace, or the measurement
and regeneration mechanisms are present but not acted on.

---

## 1. Distributed Entropy

**Description:** Every disposable capability capsule owns its own canonical database. As capsules
proliferate, the system accumulates many small databases with duplicated domain models, inconsistent
data semantics, conflicting records, and no clear ownership hierarchy.

**Why it happens:** Teams start with a single capsule that owns its data. The pattern is copied as
new capsules are created. Each capsule seems isolated. The system-wide coherence problem is only
visible when capsules need to be reconciled.

**Consequences:**
- Data inconsistencies across capsules are unresolvable without a canonical source
- Regenerating a capsule may silently lose business-critical data
- No clear answer to "what is the authoritative customer record?"
- Integration between capsules requires bespoke data mapping

**Solution:** Classify data before owning it. Canonical data belongs in durable domain APIs. See
[data-strategies.md](data-strategies.md).

---

## 2. Prompt as Specification

**Description:** The original prompt used to generate the capsule is treated as sufficient
documentation. No `intent.md` is written. No explicit contracts are defined. The tests are generated
from the implementation, not from a behavioral specification.

**Why it happens:** Prompting an AI and getting working code feels like specification. The shortcut
is tempting, especially for small features.

**Consequences:**
- When the capsule needs to be regenerated, the original prompt may be lost, outdated, or ambiguous
- There is no way to verify that the regenerated implementation matches the original intent
- Tests generated from the implementation verify implementation behavior, not business behavior
- Semantic drift is undetectable

**Solution:** Treat the durable artifacts as required deliverables, not optional documentation.
Write `intent.md` before generating. Write acceptance tests before generating. The prompt is an
input to generation; the durable artifacts are the specification.

---

## 3. Regeneration Without Tests

**Description:** The implementation is deleted and regenerated without a strong behavioral test
suite to verify correctness of the new version.

**Why it happens:** The entropy score is high. The implementation is a mess. The temptation is to start
fresh. Regeneration begins without strengthening the test suite first.

**Consequences:**
- The new implementation may not match the business behavior of the old one
- Regressions are introduced silently
- There is no way to verify that regeneration succeeded
- This is not regenerable architecture—it is undisciplined rewriting

**Solution:** Before regenerating, verify that the test suite is strong enough to catch behavioral
regressions. If it is not, strengthen the tests first. The rule: **never regenerate from weak
tests**.

---

## 4. Contract Drift

**Description:** The implementation changes its behavior without updating the public contract.
Callers continue to use the old contract definition while the implementation diverges.

**Why it happens:** The implementation is regenerated or refactored. The new implementation adds or
changes response fields, error codes, or validation rules. The contract file is not updated.

**Consequences:**
- Callers experience unexpected behavior
- Contract tests may pass because they are testing the old contract
- The contract is no longer the source of truth for caller behavior
- Trust in the contract is eroded

**Solution:** Treat contract changes as breaking changes. Use consumer-driven contract tests that
alert callers to changes. Update the contract file as a required step in any change that affects the
public API.

---

## 5. Semantic Drift

**Description:** The implementation still passes all tests, but the code no longer represents the
business intent it was created to fulfill. Domain terms have been renamed, business rules have been
reinterpreted, and the logic has drifted away from what the specification described.

**Why it happens:** Multiple generations and edits accumulate small changes. An AI tool renames a
variable for code style. A developer refactors a function without checking the intent document. The
tests are too shallow to catch the drift.

**Consequences:**
- The code is correct by its own internal logic but incorrect relative to the business
- New developers cannot map the code back to the specification
- Future regeneration will produce code that matches the current drifted state, not the original intent
- The entropy score may not reflect semantic drift if the semantic drift check is weak

**Solution:** Write tests that use domain vocabulary. Include semantic drift checks in the fitness
functions. Review `intent.md` when making changes. Use the regeneration recipe as a check: if you
regenerated from the durable artifacts today, would the result match the current implementation?

---

## 6. Nano-Service Explosion

**Description:** Every small feature or function becomes a separately deployed service. The system
has hundreds of services, each with its own deployment pipeline, monitoring, and operational
overhead.

**Why it happens:** The capability capsule concept is misread as "each capsule must be a
microservice." Teams decompose aggressively, applying the capsule boundary at the feature level
rather than the domain capability level.

**Consequences:**
- Operational overhead exceeds the value of the decomposition
- Network latency between services increases total request time
- Service discovery, authentication, and observability complexity multiplies
- The cognitive overhead of understanding the system becomes prohibitive

**Solution:** A capability capsule is a unit of knowledge preservation, not a unit of deployment. A
capsule can be a module, a package, a workflow, or a domain layer inside a modular monolith. Deploy
as a service only when the isolation genuinely justifies the cost.

---

## 7. Fitness Function Theater

**Description:** Fitness functions are created but never run. Or they run and always produce green
results because the thresholds are set too high. The entropy score is measured but never acted upon.

**Why it happens:** Adding fitness functions is visible work. Running them on a schedule and acting
on the results requires operational commitment. The measurement infrastructure is built without the
process infrastructure to respond.

**Consequences:**
- Implementation entropy accumulates without triggering any action
- The architecture has the appearance of discipline without the substance
- When a crisis occurs, the fitness functions are discovered to be miscalibrated

**Solution:** Set thresholds that reflect genuine concern. Review fitness function results in the
same cadence as other architectural reviews. Create an explicit process for what happens when the
entropy score crosses each threshold.

---

## 8. Durable Artifact Neglect

**Description:** The durable artifacts—intent documents, contracts, regeneration recipes—are created
once and never updated. Over time they describe the original implementation, not the current one.

**Why it happens:** The implementation evolves through refactoring and editing. The durable
artifacts are not code, so they are not in the change path. There is no lint or test that enforces
consistency between the implementation and the intent document.

**Consequences:**
- The regeneration recipe no longer produces correct output
- Semantic drift checks fail to detect genuine drift because they are checking against outdated intent
- New team members rely on intent documents that are no longer accurate

**Solution:** Treat durable artifact updates as required steps in change review. When a behavior
changes, the intent document, tests, and regeneration recipe must be updated in the same change set.
