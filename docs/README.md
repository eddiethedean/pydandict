# Planning documentation

This set records the Pydandict design as of 2026-09-13. It is an implementation
contract under review, not documentation for an existing release.

## Status vocabulary

- **Established requirement:** a product decision preserved from the originating
  conversation and repository request.
- **Proposed contract:** a concrete recommendation made here to resolve an
  unspecified behavior; implementation work may revise it through a decision record.
- **Prototype gate:** an unresolved feasibility question that must have evidence
  before the relevant feature or release can be claimed.
- **Observed upstream behavior:** a fact about the recorded dependency versions,
  not proof that Pydandict implements it.

Unless explicitly described as established or observed, normative API details in
this set are proposed contracts. “Must” describes an acceptance requirement, not
functionality that already exists. The [decision log](decisions/README.md) is the
authority for design status. The [mutation specification](mutation-semantics.md)
is the authority for mutator behavior; examples elsewhere must agree with it.

## Reading paths

**Evaluating the idea:** [root README](../README.md), [product](product.md),
[interoperability](interoperability.md), [competition](competitive-landscape.md).

**Implementing the core:** [decisions](decisions/README.md),
[architecture](architecture.md), [API](api.md), [mutation](mutation-semantics.md),
[nested ownership](nested-values.md), [typing](typing.md).

**Reviewing a release:** [compatibility](compatibility.md), [testing](testing.md),
[security/performance](security-performance.md), [roadmap](roadmap.md),
[contributing](../CONTRIBUTING.md), [upstream evidence](research/upstream-behavior.md).

## Requirement traceability

| ID | Established requirement | Design owner | Acceptance coverage |
| --- | --- | --- | --- |
| R1 | Package `pydandict`, primary class `DictModel` | [Product](product.md) | Packaging/import gate T1 |
| R2 | Genuine Pydantic `BaseModel` | [Architecture](architecture.md) | Type identity and schema T2, T8 |
| R3 | Real `Mapping` / `MutableMapping` participation | [API](api.md) | ABCs, iteration, consumers T2, T9 |
| R4 | Attribute and key access use the same state | [Architecture](architecture.md) | Access equivalence T2, T3 |
| R5 | Mutations preserve validation continuously | [Mutation](mutation-semantics.md), [ownership](nested-values.md) | Rollback and escaped references T3–T7 |
| R6 | Coherent Pydantic fields, extras, defaults, validators | [Mutation](mutation-semantics.md) | Policy matrix T3–T6 |
| R7 | Serializers, JSON Schema, FastAPI remain useful | [Compatibility](compatibility.md) | Differential tests T8 |
| R8 | Strong Pyright support | [Typing](typing.md) | Strict consumer tests T10 |
| R9 | Useful as a dependency for internal dictionaries | [Product](product.md), [security/performance](security-performance.md) | Consumer tests and benchmarks T9, T11 |
| R10 | Focused v1 without unrelated collections or state frameworks | [Roadmap](roadmap.md) | Scope/release review T12 |

T1–T12 are defined in the [testing strategy](testing.md). Every implementation PR
should name the relevant requirement and test group.

## Design issues that must remain visible

1. `BaseModel.__iter__` yields pairs; mapping iteration must yield keys. This is a
   deliberate behavioral and static-subtyping conflict, not solved by inheritance.
2. Full candidate revalidation can rerun transformations on unchanged values.
   Validator compatibility must be tested rather than asserted.
3. Nested guards must preserve parent invariants, rollback, serialization, and
   useful declared types without exposing an unguarded mutation path.
4. Pydantic metadata, trusted constructors/copies, cached properties, and inherited
   methods can bypass a naive mapping implementation.
5. Exact Python/dependency bounds and an open-source license are unselected.

See [roadmap gates](roadmap.md) for the next concrete work, and
[recorded probes](research/upstream-behavior.md) for what has actually been tested.
