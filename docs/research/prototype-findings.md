# Integrated prototype findings

**Project starting point: Phase 0.1, release version `0.1.0`.**
Phase 0.2 hardens and finalizes this baseline before broader release qualification.

The [executable prototype](../../prototypes/README.md) demonstrates the main G1–G3
mechanisms in one implementation. The result is a feasible conservative design for
an explicit supported envelope, not universal compatibility with every Pydantic
hook, validator or concrete Python container consumer.

That implementation is promoted into the installable [`pydandict` package](../../src/pydandict/__init__.py).
The root suite reruns the same contract against the production import; the prototype
tree remains a reproducible artifact and consumer evidence fixture.

## Evidence

The [recorded run](prototype-results.json) identifies the base Git commit, individual
prototype source hashes, exact tool/dependency versions and local artifact hashes.
The prototype was tested as working-tree changes on that base; the base commit alone
does not contain this implementation. Reproduce with
`python prototypes/run_checks.py` from the prepared environment.

- 87 runtime tests passed, with zero failures, errors or skipped cases on Python
  3.14.3. The same 87 tests passed separately on Python 3.11.14.
- The suite includes a Hypothesis state machine configured for 100 examples and
  up to 100 steps per example, plus generated append sequences and a parametrized
  list/dictionary/set method inventory. These counts are test settings, not proof
  that every possible sequence was explored.
- Failure injection covers staging, validation, result preparation and ownership
  preparation, plus failures immediately before/after selected commit-slot swaps.
  Rollback preserves live values, explicit-field metadata and retained handles;
  a subsequent valid transaction succeeds.
- Strict positive consumer typing passed. Four negative diagnostics matched their
  expected rules and source locations. Public Pyright completeness was 100% against
  the installed wheel; this measures annotations, not runtime soundness by itself.
  The implementation also passed ordinary Pyright analysis and Ruff checks.
- A mapping-only library consumer used the direct wheel; a FastAPI HTTP/OpenAPI
  consumer used the wheel rebuilt from the sdist. Both ran in separate clean
  environments outside the checkout. No external participants were needed.

The primary run used macOS ARM64, Pydantic 2.13.4/pydantic-core 2.46.4, FastAPI
0.141.1, Starlette 1.6.0, httpx 0.28.1 and Pyright 1.1.411. The two recorded
Starlette/httpx deprecation warnings remain visible. This is not a claim about
other versions or platforms, and no package was uploaded.

## Technical decisions

| Problem | Working prototype solution | Evidence / tradeoff |
| --- | --- | --- |
| Model and mapping identity | Nominal `BaseModel` plus `MutableMapping[str, object]`, explicit key iteration and transactional mutators | Runtime identity, views, dictionary unpacking, HTTP and strict consumer tests pass; one scoped iterator override suppression records the real BaseModel incompatibility |
| Atomic coupled changes | Clone raw Python state, apply a complete operation, run Pydantic on an isolated candidate, prepare all outputs, then swap owned state | The equality-constrained control rejects either first sequential assignment; the full candidate accepts the coupled update |
| Validator drift | Revalidate canonical state and reject changes to untouched state; check retained-node topology before commit | The doubling-normalizer control raises without changing live state; arbitrary non-idempotent/representation-specific validators remain outside the supported contract |
| Aliases during revalidation | Copy the generated Pydantic core schema for canonical internal validation; retain original constructors and serializers; cache explicit alias-mode variants for public validation calls | The upstream passthrough-wrap control ignored a requested name override on this pinned version; internal and public alias tests pass through the adapter |
| Ownership and escaped references | Private mutable ABC guards contain one authoritative payload; model fields reference those handles; detach incoming graphs | Saved list/dict/set/model references route to the root, preserve parent constraints and freeze boundaries, and fail after removal/replacement |
| Atomic commit with stable handles | Prepare storage pointers and metadata, retain old references during swaps, restore slots on failure | Injected failures before and after selected swaps recover; no built-in container clear/extend sequence is used as commit |
| Retained node identity | Track draft origins by object identity, reconcile at candidate positions after the requested edit, and reject unexpected retained-subtree changes | Child handles survive reorder and unrelated writes; no user equality/hash callback is used to match nodes |
| Removal return values | Prepare a detached result before committing removal; prior borrowed handles become stale | Returned lists/dicts remain editable and returned DictModels have independent validated ownership |
| Serialization and recursive schemas | An outer core-schema wrapper serializes a raw model snapshot through Pydantic; schema references belong to the outer wrapper | Field/model serializers, contexts, exclusions, computed caches, unions, generics, recursive schemas and actual HTTP responses pass |
| Metadata and lifecycle bypasses | Preserve fields-set independently, invalidate computed caches, validate copies, reject trusted construction/pickle and unsupported hooks | Default factories, resets, copy isolation, metadata snapshots and rejection/recovery tests pass |
| Root lifetime | Saved handles retain the root; the current root tracks only its current nodes | Dropping all references permits collection; all 500 replaced handles in the retention experiment were collected |

### Why container protocols are the chosen envelope

A built-in subclass with a separate live payload is unsafe for interoperability:
C consumers can inspect its unused base storage. The experiments observed empty
results from direct list/dict adapter serialization and from copying a set subclass,
despite nonempty visible values. Mirroring two writable stores would defeat the
one-state design, while mutating live built-in storage at commit reintroduces
allocation/failure hazards.

The prototype therefore uses private `MutableSequence`, `MutableMapping` and
`MutableSet` implementations. Standard annotations using these ABCs have matching
runtime interfaces and retain Pydantic list/dict/set schemas. Concrete-container
annotations also validate inputs but cannot promise concrete runtime identity.
This is a deliberate prototype scope refinement requiring explicit production
API documentation, not something to hide behind a typing completeness score.

Use `model_dump`/`model_dump_json` for serialization. Direct `json.dumps` of a guard
raises instead of silently producing an empty payload. `TypeAdapter` validation of
a guard as a collection is exercised; arbitrary standalone serializers/encoders
are not automatically supported. Plain shallow conversions can retain guarded
nested descendants, just as `dict(model)` does.

### Validator compatibility is a real constraint

Pydantic validators can transform values, depend on input representation or context,
change container topology, or run external effects. A transaction coordinator cannot
infer their arbitrary semantics or reverse external effects. The prototype does
not cache original inputs or bypass whole-model validation to mask this problem.

Supported validators are deterministic, accept canonical Python state, are idempotent
on untouched state, preserve retained mutable topology, and use no mutable private
or external state for lifetime invariants. Non-idempotent untouched scalar changes
and unexpected retained-container transformations fail before commit. A normalizer
can still run on an explicitly replaced input. Such a successful operation does
not make a non-idempotent model suitable for arbitrary later mutations.

`model_post_init`, custom initialization/finalization, private attributes and
writable properties are explicitly rejected. Validation during transactions is
Python mode with no retained request context. These restrictions are prototype
contracts; broad hook/context support remains future design work.

## Support envelope and remaining work

Supported values are exact immutable scalar/value types enumerated in the adapter,
finite lists/dicts/sets and mutable ABC fields, tuple/frozenset aggregates of safe
values, and nested DictModels. Repeated mutable aliases detach into separate owned
occurrences. Cycles, arbitrary object/custom-container values and ordinary nested
BaseModels are rejected. No configurable validation-off mode is present.

The schema wrapper, raw model allocation, fields-set restoration, compiled canonical
schema variants and storage-slot access are version-sensitive and centralized in
[the adapter](../../prototypes/pydandict_prototype/_core.py). These mechanisms need
compatibility tests on every supported upstream version before production. Schema
or class-configuration mutation after setup, custom safety-method overrides,
reflection, hostile callbacks and concurrent access are outside this experiment.
The serialization snapshot is observational; serializers must not rely on live
object identity or mutate the owning model.

The prototype treats assignment of the exact currently owned handle as an identity
no-op after the field policy check, which avoids duplicate augmented-assignment
validation. It does not distinguish a manual identity assignment from Python's
in-place writeback. That behavior needs an explicit production contract. Mutable
container iterators are conservatively invalidated after a successful container
transaction; model key iterators only invalidate when key structure changes.

| Gate / work package | Prototype outcome | Still required before a supported release |
| --- | --- | --- |
| G1 / W01 | Integrated runtime bridge, full mapping surface and consumer typing demonstrated | Supported dependency/platform matrix and final signature/API review |
| G2 / W02 | Atomic candidate/commit, metadata, aliases and failure recovery demonstrated within the validator contract | Broader hook decisions, upstream-version qualification and safety audit |
| G3 / W03 | Owned finite trees and stable handles demonstrated with protocol guards | Finalize concrete-container expectations, complete production envelope and adversarial coverage |
| W04 | One implementation passes nested mutation, types, serializers/schema and HTTP together | Review these explicit scope decisions before promoting production internals |
| G4 | Runtime tests on Python 3.11.14/3.14.3, artifact qualification on 3.14.3, one dependency stack/platform | Additional advertised Python versions, dependency boundaries and platforms |
| G5 | Local experimental artifacts build and install; root package metadata and MIT license are now present | Package-name ownership, private security reporting and public release process remain open |

## Initial costs

The recorded scalar-write workload changes one scalar while retaining a list of
10, 100 or 1,000 integers. Median write times were approximately 0.12 ms, 0.33 ms
and 2.37 ms respectively. Mean key-read time was about 0.40–0.43 microseconds in that
run. Traced peak allocations for one write were about 29 KB, 31 KB and 133 KB.
These are local feasibility observations with 30 timing samples after five warmup
writes, not production budgets or comparisons with equivalent competitor guarantees.

Full-root cloning/revalidation scales with graph size. The conservative prototype
makes multiple isolated copies and performs structural checks; large/deep models
will cost more. Production work should measure broader workloads and reduce redundant
copying only while preserving the rejection and ownership tests. No speed claim or
release budget is inferred from this single-machine sample.
