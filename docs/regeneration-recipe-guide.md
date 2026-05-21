# Regeneration Recipe Guide

A guide for tech leads writing their first regeneration recipe.

---

## What a recipe is

A regeneration recipe is a version-controlled document that tells an AI tool — or a developer — how
to recreate a capsule's implementation from its durable artifacts. It is the answer to: "If I
deleted all the source code right now, what would I need to know to get back to a correct
implementation?"

The recipe is not a prompt. It is not boilerplate. It is not a wishlist of best practices. It is
an explicit, opinionated set of instructions specific to this capsule, informed by what the
capsule's previous regenerations got wrong.

A good recipe is the most informed document in the repository about the hard parts of this
particular capsule. A bad recipe is generic advice that could describe any project.

---

## What a recipe is not

**It is not an AI prompt.** An AI prompt is a one-time, disposable input. A recipe is a durable
artifact that will be maintained, versioned, and improved over years of regeneration cycles.
Write it for the engineer who will read it in two years and ask "why does it say that?"

**It is not a specification.** The specification is `intent.md` and the tests. The recipe is
instructions for *how to regenerate correctly*, given that the specification already exists. A
recipe that duplicates the specification is a recipe that will drift from the specification.

**It is not boilerplate.** A recipe that says "follow best practices," "write clean code," or "make
sure tests pass" contains no information. Every section must earn its place by capturing something
specific to this capsule that a generator would not know from the durable artifacts alone.

---

## What makes a recipe good

**Specific.** Instead of "implement the business rules," say "apply the 15% cap after summing all
applicable discounts, not before." Instead of "don't add unnecessary dependencies," say "do not add
requests, httpx, or pydantic — this capsule's test suite has no such dependencies and adding them
breaks the repository's dependency model."

**Falsifiable.** Every constraint should be checkable. If you can't tell from reading the
generated code whether the constraint was followed, it is not specific enough. "No caching" is
checkable. "Write maintainable code" is not.

**Opinionated about what has gone wrong.** The most valuable sentences in a recipe are "previous
generators have done X, which breaks Y." This is knowledge that cannot be derived from the durable
artifacts. A recipe that does not reflect the actual failure history of this capsule is not as
useful as one that does.

**Short enough to be read.** A recipe that no one reads before regenerating is not a recipe — it
is documentation debt. Keep each section tight. A constraint list of ten items means the
capsule is too complex, not that the recipe should be longer.

---

## What makes a recipe bad

**Vague.** "Use the intent document as the source of truth" does not help a generator that already
intends to do this but doesn't know which specific passage to use, or which invariant is the tricky
one.

**Generic.** If the recipe could describe any capsule in the repository, it adds nothing. Cut the
generic advice. The generator already knows to pass tests. What it does not know is the specific
way this capsule's logic has historically been misimplemented.

**Incomplete inputs.** A recipe that does not list every input artifact — including which are
primary and which are constraints — forces the generator to make assumptions. Those assumptions are
where regeneration failures originate.

**No hazards section.** The "Known regeneration hazards" section is where a recipe earns its value.
If it is empty or contains only "make sure tests pass," the team has not yet used the recipe
seriously. Every failed regeneration should produce at least one new entry.

---

## The required sections

A complete recipe has these seven sections. All are required.

### 1. Purpose

One paragraph. What does this capsule do? What does the recipe produce? Who reads this?

### 2. Inputs

Two subsections:
- **Primary inputs**: artifacts that specify behavior. The generated implementation must satisfy
  them in full. List file paths and the role of each.
- **Constraint inputs**: artifacts that constrain implementation choices without fully specifying
  behavior. List file paths and what they constrain.

The distinction matters: a constraint input failing to be satisfied is a configuration problem; a
primary input failing is a behavioral regression.

### 3. Generation steps

Ordered, numbered, concrete steps. Not "generate the implementation." Concrete steps like:
"Read the outbound contract in `dependencies.yaml` and note the exact response fields the
implementation may consume. Do not consume fields not listed there." Each step should be short
enough to follow and specific enough to be checkable.

### 4. Constraints and prohibitions

A short list of things the recipe forbids. This section exists for things the durable artifacts do
not explicitly prohibit but that experience shows generators get wrong. Three to eight items is a
good range. More than ten items suggests the capsule needs to be reconsidered structurally.

Write each constraint as a prohibition with a reason. "No caching" is insufficient. "No caching of
discount results — previous generations introduced memoization that broke the isolation guarantee
callers depend on" is complete.

### 5. Verification

What must pass after regeneration. Be explicit:
- Which test commands, with their expected outcomes
- Which fitness function commands, with their expected outcomes
- Which manual checks (reading the implementation against intent, confirming specific behaviors)

Verification is not "run the tests." It is "run these tests, confirm this behavior, confirm the
implementation vocabulary matches these specific terms."

### 6. Known regeneration hazards

A short list of things that have gone wrong or are predicted to go wrong. This is the most
valuable section in the recipe and the one most commonly neglected.

Format: `[Historical]` for failures that have actually occurred, `[Predicted]` for failures
predicted based on the capsule's structure. Mark all entries so that readers know the confidence
level.

Every failed regeneration should produce a new entry here. The entry should name the symptom
("the generator imported calculate_discount directly instead of using the injected callable"),
describe the failure mode ("acceptance tests still passed, masking the violation"), and give the
fix ("add explicit instruction: use only the discount_service parameter").

### 7. Last-regenerated metadata

Date, model used, prompt version reference. This makes the recipe auditable and enables teams
to correlate regeneration quality with model changes over time.

---

## How recipes evolve

A recipe written before the first regeneration is an educated guess. It is worth writing, but
it will be wrong about some things.

After the first regeneration, the recipe should be updated with whatever was discovered: a
constraint that needed to be added, a verification step that caught a problem, a hazard that
materialized. After the second, it improves again. By the third, the recipe is a genuine asset.

The rule: **every failed regeneration must produce at least one new entry in "Known regeneration
hazards."** If it does not, the team is discarding knowledge that cost them time to acquire.

Recipes are not maintained between regenerations in the way that `intent.md` and tests are. They
do not need to be updated when business rules change. They need to be updated when regeneration
experience changes — when a new failure mode is discovered, when a constraint is found to be
necessary, or when a verification step is found to be insufficient.

---

## The recipe and the LLM that uses it

The recipe is the durable artifact. The LLM is the disposable executor.

This means: if a regeneration fails because the LLM did not follow the recipe, the answer is to
strengthen the recipe, not to retry with a better prompt. The recipe should be specific enough
that the failure is preventable in the next regeneration, not just avoided in this one.

The LLM's output — the generated source code — is verified against the durable artifacts (tests,
contracts, signal dashboard). It is not verified against the LLM's own confidence. If the generated
code does not pass the verification steps, it is wrong regardless of how confident the LLM was.

The recipe does not need to explain why the business rules exist — that is `intent.md`'s job. The
recipe explains why specific constraints exist and why specific hazards occur. The reader of the
recipe already has `intent.md`; they need the recipe to tell them what `intent.md` does not say.

---

## Quick reference: recipe quality checklist

Before considering a recipe complete, confirm:

- [ ] Every constraint has a reason — not just "don't do X" but "don't do X because Y happened"
- [ ] The verification section lists specific commands and expected outputs, not just "run the tests"
- [ ] The inputs section distinguishes primary from constraint inputs
- [ ] The hazards section has at least one entry (even if predicted)
- [ ] No section contains advice that could apply to any capsule in the repository
- [ ] A competent engineer could follow the recipe to a passing regeneration without asking anyone questions

The last check is the most important. Read it as if you are the engineer who will use this recipe
in two years, with no memory of the current implementation. Would you know what to do?
