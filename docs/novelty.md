# Novelty: What Is and Is Not New

Regenerable Architecture is honest about its ingredients. Most of them exist already. The novelty is the synthesis and the lifecycle it creates for AI-assisted systems.

## What Is Not New

### Evolutionary Architecture

Neal Ford, Rebecca Parsons, and Patrick Kua's work on evolutionary architecture established that architectural fitness functions should be automated, that systems should be designed to accommodate change, and that guided evolution is preferable to big-bang redesign.

Regenerable Architecture uses fitness functions directly and shares the evolutionary architecture commitment to continuous measurement. The difference is that regenerable architecture targets AI-era implementation decay specifically, and treats regeneration—not just refactoring—as a first-class lifecycle event.

### Architectural Fitness Functions

Fitness functions—automated checks that evaluate whether a system meets architectural goals—are the core measurement mechanism in regenerable architecture. This is not new. What is new is applying fitness functions to AI slop signals specifically.

### Contract-First Development

Designing the API contract before implementing it is well-established practice. Regenerable Architecture elevates contracts from design technique to durable artifact—one of the sources of truth from which implementation is regenerated.

### Consumer-Driven Contract Testing

Pact and similar tools establish that the consumer, not the producer, should define the contract. This informs the contract durability strategy: contracts must represent genuine consumer commitments, not implementation convenience.

### Disposable Architecture

The idea of building services designed to be thrown away has been discussed in infrastructure (immutable servers, cattle not pets) and in some microservice architectures. Regenerable Architecture formalizes the lifecycle that makes disposability safe: you can only safely dispose of something when you have preserved everything needed to recreate it.

### Microservices

Capability capsules are not microservices. But microservice thinking—explicit boundaries, clear contracts, independent deployability—informs capsule design. The key difference: a capsule does not have to be a service. It is a unit of knowledge preservation and regeneration, not a deployment unit.

### Modular Monolith

Capsules can live inside a modular monolith. The modular monolith provides the right level of isolation without service-call overhead. Regenerable Architecture works within this structure.

### Code Generation and Scaffolding

Code generation from specifications is not new—OpenAPI generators, gRPC stubs, and scaffold tools have existed for years. Regenerable Architecture extends this to AI-driven generation from richer intent artifacts, and adds the measurement and regeneration lifecycle around the generated output.

### Event Sourcing

Event sourcing makes state reproducible by replaying events. This same principle—state as a projection of durable history—informs the capsule data strategy. If a capsule's local state can be rebuilt from events, the capsule becomes more safely disposable.

### CQRS

Separating command and query responsibilities helps define which parts of a capsule's behavior are canonical and which are projections. Projections can be discarded; commands must preserve invariants.

### Immutable Infrastructure

The "cattle not pets" philosophy for infrastructure—replace rather than patch—applies directly to implementation code in regenerable architecture. The implementation is cattle; the durable artifacts are the ranch.

### Infrastructure as Code

IaC preserves the intent and specification of infrastructure in version-controlled artifacts. Regenerable Architecture applies the same logic to application code: the specification is durable; the generated output is reproducible.

### Data Mesh and Data Products

Data mesh establishes that data should have clear domain ownership, quality contracts, and self-service discoverability. This directly informs the data strategies for capsule systems: canonical data must be owned by durable domain APIs, not disposable capsules.

### Property-Based Testing

Property-based tests express invariants that must hold for all inputs, not just specific examples. These are exactly the kind of tests that should survive regeneration—they specify what is always true, regardless of implementation.

### Golden-Master Testing

Golden-master (snapshot) testing captures existing behavior as a baseline. This is useful after regeneration: compare new output against the preserved golden master to detect behavioral drift.

## What Is New

The novelty is the synthesis of these ideas into a coherent **AI-era lifecycle**:

```
Specify → Generate → Operate → Measure Slop → Regenerate
```

Specifically, what is new:

1. **AI slop as a named, measurable architectural phenomenon**. The specific failure mode of AI-generated implementation decay—complexity accumulation, semantic drift, duplicated patterns—is not well-addressed by existing architectural frameworks.

2. **The regeneration lifecycle as a first-class architectural pattern**. Existing architecture frameworks treat rewriting as failure. Regenerable Architecture treats it as a planned, tool-supported lifecycle event.

3. **The slop score as a fitness function for AI-specific decay**. Combining complexity, duplication, dependency growth, semantic drift, and test confidence into a composite signal that triggers regeneration is novel.

4. **The capability capsule as the unit of knowledge preservation**. The capsule bundles everything needed to specify, generate, and regenerate a capability. This is more than a microservice or a module—it is a self-describing, regenerable unit.

5. **The regeneration recipe as a first-class artifact**. Explicit instructions for how to use AI tools to recreate the implementation are not part of any existing architecture framework.

## The Differentiator in One Sentence

> Regenerable Architecture is specifically about designing AI-assisted systems so that generated implementation can be safely discarded and recreated from durable architectural knowledge.

This sentence cannot be said about evolutionary architecture, disposable architecture, contract-first design, or any other adjacent concept in isolation. The synthesis is the contribution.
