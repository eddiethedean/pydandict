# Design decisions and open gates

The originating conversation established the package's identity, model/mapping
bridge, continuous validation goal, Pyright priority, and narrow scope. It did
not settle every operation. This log distinguishes those requirements from the
recommendations added in this planning set.

| ID | Decision | Status | Rationale and consequence |
| --- | --- | --- | --- |
| D01 | `pydandict` / Pydandict / `DictModel` | Established | One clear public primitive |
| D02 | Genuine `BaseModel` plus mapping protocols; no built-in `dict` inheritance | Established | Preserve ecosystem identity and generic mapping interoperability |
| D03 | Attribute and mapping access share authoritative model state | Established | Avoid a backing-dict/model synchronization problem |
| D04 | Validate all supported mutation paths continuously | Established | Internal dictionaries must remain valid, including nested state |
| D05 | Pyright and `Mapping` / `MutableMapping` compatibility are first-class | Established | Runtime duck typing alone is insufficient |
| D06 | No unrelated collections, persistence, or reactivity in v1 | Established | Keep a focused dependency |
| D07 | Canonical field names are mapping keys; aliases stay at input/output boundaries | Proposed | Prevent duplicate key identities and ambiguous writes |
| D08 | All declared fields remain present; delete/pop cannot remove them; `reset` restores defaults | Proposed | Removing then reintroducing a default is misleading mapping behavior |
| D09 | Validate isolated candidate state and commit once | Proposed; prototype required | Assignment validation alone does not provide rollback or atomic multi-field updates |
| D10 | Default `extra='forbid'`; configurable allow/ignore input; unknown mutations rejected unless allow | Proposed | Match assignment-style semantics and avoid silent typo writes |
| D11 | Mapping values use `object`; attribute types remain specific | Proposed | Honest heterogeneous typing without spreading `Any` |
| D12 | Preserve Pydantic equality; iteration changes to keys; mutable instances unhashable | Proposed | Model identity/metadata equality remains useful; mapping equality is a documented divergence |
| D13 | Private guards for owned nested values; reject unprotectable mutability | Proposed; release gate | Meet lifetime validation without a public collection framework |
| D14 | Validate `model_copy(update=...)`; reject public `model_construct` in v1 | Proposed | Close named public construction/copy bypasses; document narrower BaseModel API |
| D15 | No configurable validation-off mode for `DictModel` | Proposed | Avoid two safety levels under one type |
| D16 | Qualify releases against a measurable quality bar and commit-specific evidence | Proposed | Correctness, typing, integration, performance and packaging need inspectable results, not milestone labels |
| D17 | Integrate G1–G3 in one vertical slice before choosing production internals | Proposed | Successful isolated prototypes may have incompatible transaction, type or serialization assumptions |
| D18 | Use automated isolated consumer projects and maintainer walkthroughs; require no external trials or participants | Established constraint | The user explicitly requires qualification without involving other people; this supplies reproducible integration evidence without claiming independent adoption research |
| D19 | Return detached usable mutable values from successful removal; invalidate prior borrowed handles | Proposed; G3 evidence required | `pop`/`popitem` must not return immediately stale handles; prepare return values before commit for failure safety |

## Phase 0.1 decisions

| ID | Decision | Status | Rationale and consequence |
| --- | --- | --- | --- |
| D20 | Use private mutable ABC guards with one payload per node; recommend matching ABC field annotations | Demonstrated prototype choice; production contract review in 0.2 | Built-in subclass buffers can be read directly by ordinary C consumers; protocol guards avoid silent empty data and permit pointer-swap commits |
| D21 | Centralize raw snapshots, canonical core-schema variants, outer schema references and serializer delegation in the prototype adapter | Demonstrated on the pinned upstream stack; production matrix open | Resolves isolated validation, alias-wrap behavior and recursive serialization without a parallel validation engine |
| D22 | Treat the integrated prototype and promoted root package as Phase 0.1 and the project's starting baseline | Established | The user explicitly selected this baseline; Phase 0.2 hardens/finalizes it while retaining the tests and working mechanisms |

The [findings](../research/prototype-findings.md) describe the validator restrictions,
identity-writeback behavior, root retention and concrete-container limitations.
Baseline acceptance does not silently turn these experimental choices into a
universal Pydantic compatibility promise.

## Alternatives considered

**Wrap a `RootModel[dict]`:** useful for homogeneous mappings, but does not directly
make individually declared model fields into keys. It remains an alternative for
users who do not need Pydandict's lifecycle contract.

**Return `model_dump()` for every mapping operation:** would invoke serialization,
possibly rename/exclude fields, and detach data from model state. Rejected for reads
and transaction input.

**Delegate all writes to `setattr`:** useful prototype baseline, but cannot ensure
rollback, atomic `update`, nested mutation interception, or parent invariants.

**Delete a defaulted field by resetting it implicitly:** leaves the supposedly
deleted key present. The proposed contract instead rejects field deletion and
gives resetting an explicit name. This refines the early exploratory `pop` example;
requiredness and default semantics were requirements, its exact mechanism was not.

**Type all mapping operations as `Any`:** easier signatures, but loses the user's
Pyright objective. A heterogeneous base class cannot automatically express a
different return type for every subclass field name.

**Copy on every nested read:** protects the original but silently makes
`model.tags.append(...)` mutate a detached value. Rejected as the default semantics.

**Public validated collection family:** unnecessary scope growth. Internal guards
may exist only to enforce model ownership, with no public `TypedList`/`TypedMap` API.

## Open gates

G1–G3 now have integrated Phase 0.1 evidence within the
[prototype envelope](../research/prototype-findings.md). The table records what
still needs production qualification; it no longer means there is no experiment.

| Gate | Concrete question | Evidence required | Blocks |
| --- | --- | --- | --- |
| G1 | Can nominal mapping inheritance coexist with model serialization and useful Pyright signatures? | Runtime/FastAPI spike and strict typing fixtures, including the iterator conflict | First alpha |
| G2 | Can isolated revalidation preserve validators, aliases, fields-set, frozen fields, and model hooks? | Transaction prototype, differential tests, explicit unsupported cases | First alpha |
| G3 | Can nested guards preserve declared types, root invariants, escaped references, and serialization? | Mutation-path inventory plus adversarial ownership tests | Lifetime guarantee and v1 |
| G4 | Which Python, Pydantic, FastAPI, and Pyright versions pass the matrix? | CI results with exact versions and boundary tests | Every release |
| G5 | What license and distribution metadata should be adopted? | Maintainer-selected license, name availability, metadata review | Distribution |

Execution mapping: W01–W04 are demonstrated in the Phase 0.1 baseline; Phase 0.2
reviews and hardens their production implications. G1/G2 need qualification for the
first scalar alpha; G3 needs production qualification at W09 before nested support
is advertised. G4 applies to every distribution; W05 must resolve G5 before the
first distribution. The [work packages](../implementation-plan.md) and
[quality bar](../quality-bar.md) define required outputs and evidence.

Maintain decisions in this log until a choice requires a substantial separate
record. A revision must state the trigger, alternatives, compatibility impact,
and tests; do not silently turn a prototype limitation into a product promise.
