# Phase 0.3 — Architecture and implementation contract

Status: **READY FOR IMPLEMENTATION**. This document defines a planned change;
it does not claim Phase 0.3 implementation, qualification or publication.

This is the implementation and review boundary for the
[minimal scalar core milestone](../ROADMAP.md#03--minimal-scalar-core), covering
W05 qualification and W06–W07 in the [work packages](implementation-plan.md).
Acceptance IDs below are local to Phase 0.3; cite them as `0.3/AC-001`, etc., to
distinguish the [completed Phase 0.2 contract](phase-0.2-plan.md).
Required behavior in this document governs this change. Existing Phase 0.2
contracts remain compatibility requirements unless an explicit correction below
changes them. Older first-package and unresolved-license wording is historical,
not a reason to recreate the package or reopen settled decisions.

## Architecture summary

Retain `DictModel` as a genuine `BaseModel` and `MutableMapping[str, object]`.
Harden and qualify scalar records using the existing isolated-candidate,
canonical whole-root validation and prepared storage-swap transaction engine.
There must be one authoritative Pydantic state, not a synchronized second store.
Serialization must never supply transaction input.

Phase 0.3 is a **scalar qualification boundary**, not a new scalar-only runtime
mode. Phase 0.2 already shipped supported nested values. Do not remove those
values, disable their guards, or reject supported mutable input merely to make
the scalar milestone smaller. Retain their existing regression suite. New
ownership mechanisms, nested-envelope expansion and broader ecosystem work
remain Phase 0.4 tasks. Release descriptions must distinguish scalar-core
qualification from inherited, bounded Phase 0.2 nested support; neither justifies
a lifetime guarantee for arbitrary nested Python data.

### Repository ground truth

Inspected on 2026-09-14 at commit
`1ed7dcce53cb7db946dd233dd56e4a55e0236019`; the worktree was clean before planning.
No applicable `AGENTS.md` was found in the repository or its parent chain.

| Surface | Observed baseline |
| --- | --- |
| Package | `src/pydandict/__init__.py` exports only `DictModel`; `py.typed` exists. Metadata declares version `0.2.0`. |
| Core | `_core.py` already implements reads, namespace checks, all mapping mutators, reset, metadata snapshots, validated copies, schema hooks and trusted-path rejection. Snapshot/reconciliation/transaction helpers remain in this module. |
| Adapter | `_compat.py` owns version-sensitive state/schema access, allocation, storage swaps/restoration, canonical/entry validators, serializer delegation and class-local caches. It explicitly accepts only Pydantic `2.13.4`. |
| Nested baseline | `_containers.py` provides private owned mutable ABC guards. Concrete list/dict/set field annotations are rejected; ordinary list/dict/set inputs remain supported under the existing envelope. |
| Existing tests | `test_prototype.py` covers scalar bounds, reads, rollback, extras, defaults, copies, lifecycle and nested behavior. `test_inventory.py` adds alias/default/property/cache cases; `test_stateful.py` exercises mixed nested transactions. Phase 0.2 contract and remediation/re-review tests protect prior fixes. |
| Types and consumers | `tools/check_typing.py` checks strict production source and exact expected negative diagnostics. `tools/qualify_package.py` builds direct and sdist-rebuilt wheels, checks isolated imports, library/HTTP consumers, metadata snapshots, marker and installed typing. |
| Packaging | setuptools `>=77`, Python `>=3.11`, classifiers 3.11–3.14, MIT with packaged license, sole direct runtime dependency `pydantic==2.13.4`. Pydantic's transitive dependencies are not additional direct package requirements. |
| Development dependencies | FastAPI `0.141.1`, httpx `0.28.1`, Pyright `1.1.411`; build, Hypothesis, pytest, Ruff and Twine are development tooling. |
| CI | Reusable `check.yml`: Linux Python 3.11/3.12/3.13/3.14; macOS and Windows 3.11/3.14; lint/format, runtime, typing and completeness gates. Ubuntu 3.11/3.14 additionally qualify artifacts and run benchmarks. |
| Release | Tag-triggered checks, package preflight, version equality, build/Twine checks and Trusted Publishing. The workflow does not publish TestPyPI or create GitHub Releases. |
| Persistence/security | No persistence or migration engine. Pickle and trusted construction are disabled. `SECURITY.md` names private reporting and maintainer triage; the GitHub private-reporting API returned `enabled: true`. |

Inspected specifications: [API](api.md), [mutation semantics](mutation-semantics.md),
[architecture](architecture.md), [compatibility](compatibility.md),
[typing](typing.md), [testing](testing.md), [product](product.md),
[quality bar](quality-bar.md), [security/performance](security-performance.md),
[release](release.md), [decisions](decisions/README.md), README examples, existing
consumer fixtures and the [sixth Phase 0.2 review](reviews/phase-0.2-rereview-6.md).
Historical review/release evidence is not fresh Phase 0.3 evidence.

Planning checks used macOS/CPython `3.11.14`, Pydantic `2.13.4`, pydantic-core
`2.46.4`, FastAPI `0.141.1`, Starlette `0.48.0`, httpx `0.28.1`, pytest `9.1.1`,
Hypothesis `6.151.9`, Pyright `1.1.411` and Ruff `0.15.6`.
The local installed distribution metadata still reports `0.1.0`; source checks
therefore used `PYTHONPATH=src`. That environment mismatch is not a source-version
defect and cannot serve as 0.3 artifact evidence. Future artifact checks must
install freshly built distributions in external clean environments.

Baseline checks performed during planning:

- Documentation: 37 Markdown files, 232 local links, eight Python examples; zero errors.
- Strict positive/negative typing: pass; public completeness: 100%, resolved to `src/pydandict`.
- Required Ruff lint/format: pass; 24 files already formatted.
- Full production runtime suite: 151 passed in 103.50 seconds.
- No new clean-artifact build, full CI matrix, publication or performance measurement was performed for this plan.

### Confirmed scalar gap

On the inspected source, `Scalar().pop(1, 'fallback')` returns the fallback and
`Scalar().pop(1)` raises `KeyError`. Deletion, setdefault and reset already reject
the integer key with `TypeError`. This conflicts with the documented mutation-key
contract. Correct `pop` to reject every non-string key before missing-key/fallback
handling; record the correction in migration notes. Read APIs retain their
documented non-string behavior. This defect is in scope, not a release exemption.

## Change boundary

**Problem.** The scalar API exists, but the roadmap does not yet define a bounded,
complete W06/W07 qualification contract. Existing scalar tests are distributed
through mixed nested fixtures; method/key/error interactions need an explicit
coverage matrix, and `pop` has a confirmed key-policy inconsistency. Some planning
documents still describe already-completed packaging/license decisions as open.

**Desired outcome.** Scalar records have a precise read, mutation, default,
metadata, freeze, copy and error contract, demonstrated by focused tests and
installed consumers on the existing matrix. Unsupported values cannot enter live
state; the shipped nested baseline remains intact. Docs accurately identify the
qualification envelope and the next milestone.

**In scope:** scalar T1–T6/T10, read-side T9, the scalar serialization needed to
demonstrate G1/G2, focused adversarial/stateful/fault tests, correction of confirmed
scalar defects, installed scalar examples/consumers, exact support metadata and
G4/G5 evidence. Reconcile only documentation affected by this milestone.

**Touched surface:** `_core.py` scalar methods/policy/helpers; `_compat.py` only
if a demonstrated scalar correction needs adapter work; `tests/` scalar contracts
and typing fixtures; `tools/qualify_package.py` and typing helper if fixtures change;
a runnable scalar example; README, API/mutation/compatibility/testing/typing/release
docs, roadmap/backlog/decisions and changelog as needed. `pyproject.toml` and
`check.yml` may change only for necessary qualification wiring/metadata accuracy.
No change to `_containers.py` is expected; touching it requires a demonstrated
in-scope regression and preserves its existing contract.

**Not authorized by this plan:** release tags, pushes, publication, repository
settings changes, issue closure, or enabling new services. Package version stays
`0.2.0` during implementation; write changes under `Unreleased`. Preparing an exact
`0.3.0` candidate and distributing it are separately initiated release operations.

## Public contract — required behavior

### Scalar qualification envelope

Qualified stored values are exact `None`, `bool`, `int`, `float`, `str`, `bytes`,
`Decimal`, `date`, `datetime`, `time`, `timedelta` and `UUID`. For datetime/time,
tzinfo is absent or an exact `datetime.timezone`. Preserve Pydantic constraints,
strictness and mode-specific coercion. Do not add a blanket finite-number rule:
NaN/infinity remain subject to the schema, not an invented package restriction.

Qualify plain leaf annotations, nullable/scalar unions, scalar `Literal`,
`Annotated` constraints and canonical-safe validators, forward references resolving
to these annotations, and explicitly specialized scalar generic models. `Any`,
`object` and allowed untyped extras qualify when their resulting stored values are
scalar leaves. Typed extras retain the supported outer declaration
`__pydantic_extra__: dict[str, V]`, with scalar `V` for this matrix.

Tuples/frozensets, models and owned ABC collections are not scalar leaves; retain
their Phase 0.2 behavior and regression coverage, without adding new 0.3 support
claims. No scalar flag, new base class or separate validation engine is introduced.
Arbitrary objects, custom scalar subclasses/enums, secret wrappers, ordinary
BaseModels, custom timezones and unsupported mutable values remain outside the
existing closed envelope and must fail before escaping construction or commit.
Existing schema rejection vs runtime-value rejection timing is preserved.

### Construction, extension and configuration

Keep the sole import `from pydandict import DictModel`; ordinary Pydantic field
declarations, keyword construction, `model_validate`, `model_validate_json` and
`model_validate_strings` remain available. There is no positional-dict constructor.
Existing-model validation must detach before callbacks and must not mutate its
source on success or failure. Qualify ordinary `TypeAdapter` scalar paths as well.

Defaults remain `extra='forbid'`, `validate_assignment=True`,
`validate_default=True`, `revalidate_instances='always'`. Class/field attempts to
disable required validation fail. Construction respects supported allow/ignore/
forbid input policy; mutation never silently ignores unknown keys. Reject stored
extras inconsistent with the ongoing class policy after one-off input overrides.

Keep the Phase 0.2 hook restrictions: no custom initialization/finalization,
`model_post_init`, private schema state or writable properties. Preserve supported
read-only properties, computed fields and serializers as observational features,
not mapping entries. Safety-critical subclass overrides and schema mutation after
instances escape are outside the guarantee. Scalar schema rebuild before use must
retain class-local validator-cache invalidation; do not broaden dynamic-schema use.

Supported validators remain deterministic, schema-sound, canonical-state-safe and
idempotent; model-after validators return the candidate. Public construction may
receive context; mutation and validated copy use Python mode with `context=None`.
Do not retain construction context. Untouched scalar drift must fail before commit
with `pydandict_canonical_drift:`. No guarantee of exactly one invocation of every
user callback is added; there is one whole-root transaction, not repeated public
assignments. Programming exceptions propagate rather than becoming validation errors.

### Namespace and reads

Mapping keys are declared canonical fields in Pydantic field order, followed by
stored extras in insertion order. Defaults and excluded fields are present.
Aliases are input/output names only. Replacing a value does not move its key;
removing and reinserting an extra appends it.

Reject method/model namespace collisions, underscore-prefixed stored names,
computed/property collisions, ambiguous emitted aliases and extras colliding with
emitted aliases under the existing Phase 0.2 policy. External aliases may resemble
methods when their canonical field names are safe. Do not make aliases alternate
mapping addresses. Custom serializers remain responsible for their own output.

| API | Required result |
| --- | --- |
| `m[key]` | Stored Python value; missing/non-string key raises `KeyError`, including an unhashable non-string key. |
| `m.field` | Same authoritative field value; missing attribute raises `AttributeError`. |
| `iter(m)`, `len(m)`, `bool(m)` | Canonical string keys; number of fields plus extras; truth follows length. |
| `key in m` | Key membership; false for absent/non-string keys. |
| `m.get(key, default)` | Stored value or exact fallback object, without insertion/default validation. |
| `keys`, `values`, `items` | Live `KeysView[str]`, `ValuesView[object]`, `ItemsView[str, object]`. |
| `dict(m)`, keyword unpacking, mapping patterns | Ordinary mapping behavior, not serialization. |

Model key iterators capture ordered-key structure at iterator creation, including
before the first `next`. A committed local key addition/removal/order change
invalidates an unexhausted iterator with `RuntimeError` and
`pydandict_iterator_invalidated:`. Value-only commits, failed operations and empty
no-ops do not invalidate it. Exhausted iterators remain exhausted. Values/items
views expose current committed values without multi-read snapshot guarantees.
Retain D26's separate container iterator policy unchanged.

Preserve Pydantic model equality rather than equality with arbitrary dictionaries.
Mutable models are unhashable; scalar frozen models follow the supported
Pydantic-compatible hash behavior. No custom hash cache is introduced.

### Mutation, return values and errors

Retain existing signatures and ABC-compatible types: item/attribute assignment,
`update(other=(), /, **kwargs)`, `__ior__`, deletion, `pop`, `popitem`, `clear`,
`setdefault`, `reset(*field_names)` and validated copy APIs. Mapping reads/writes
remain heterogeneous `object`; normal attribute inference remains field-specific.
Copy returns `Self`; views carry string keys and object values.

All mutating key/name arguments must be strings, including `pop` with a fallback.
Non-string arguments raise `TypeError`; where library-generated, retain
`pydandict_protected_name:`. Read-side non-string behavior is different by design.
Do not convert non-string names, resolve aliases, or validate unused fallbacks.

| Operation | Required behavior / return |
| --- | --- |
| Item/attribute set | One validated transaction; returns None; both syntaxes produce identical state and validation failures. Equal scalar assignment is still a write request. |
| `update`, `|=` | Fully consume mapping or iterable of pairs before validation; last duplicate wins, keyword entries win; one atomic whole-model change. `update` returns None; `|=` returns the same instance. `update(m)` works. |
| `setdefault` | Existing string key returns its stored value without validating unused default or invoking validators. Missing allowed key inserts and returns the coerced committed value. |
| `del`, `pop` | Only remove extras; every declared field remains protected, defaulted or nullable included. `pop` returns removed scalar or exact fallback only for an absent string key. |
| `popitem` | Attempt the last key, never skip a protected field; return `(key, value)`, or `KeyError` on empty model. |
| `clear` | Remove all entries atomically; reject if declared fields exist. A fieldless model's validators may reject clearing extras. Empty clear is a no-op. |
| `reset` | Deduplicate names in first-occurrence order; atomically reevaluate only selected declared defaults in Pydantic field order. Missing name: `KeyError`; required/extra name: reset-policy `ValidationError`. No names: no-op. |

Malformed bulk pair input retains Python's `TypeError`/`ValueError` distinction.
A generator failing after valid pairs must not partially apply them. The same-root
guard must be acquired before consuming user input or invoking candidate callbacks.
Malformed call/input and non-string key errors precede policy/validation errors;
after materialization, existence and write policy precede full-schema validation.
Do not introduce a promise to aggregate all independent policy failures.

Missing deletion/pop and empty popitem retain `KeyError` even on frozen models;
attribute missing deletion translates to `AttributeError`. Present frozen state
rejects actual write/removal/reset requests, even equal scalar writes. Existing-key
setdefault, missing-pop fallback and empty update/reset/clear are no-ops on frozen
models. A mixed frozen/unfrozen bulk request commits nothing.

Retain stable policy codes: `extra_forbidden`, `frozen_instance`,
`pydandict_field_deletion`, `pydandict_reset_required` in `ValidationError` details;
retain relevant canonical key locations and Pydantic's value-validation details.
Keep `pydandict_protected_name:`, `pydandict_unsupported_annotation:`,
`pydandict_unsupported_value:`, `pydandict_unsupported_configuration:`,
`pydandict_trusted_path_disabled:`, `pydandict_incompatible_pydantic:` and
`pydandict_canonical_drift:` TypeError prefixes. Same-root mutation/copy reentrancy
remains `RuntimeError` with `pydandict_reentrant_transaction:`.
Exact upstream English messages are not compatibility promises.

### Defaults, metadata, caches and copies

Validate all materialized defaults. Reset factories receive preceding validated
candidate fields as Pydantic defines; unrelated factories are not regenerated.
Factory/validator exceptions leave live state intact; do not retry callbacks.

Preserve omitted default fields as absent from `model_fields_set`; successful
explicit writes mark only assigned names, reset removes selected explicit marks,
extra insertion/removal updates extra marks under the supported upstream rules.
Full candidate validation must not mark every visible default explicit.
`model_extra` is a detached plain dictionary or None; `model_fields_set` is a
detached plain set. Editing these snapshots must not change stored state.
Invalidate supported cached computed values on successful commits, but preserve
them on failed/no-op operations. Arbitrary external caches remain unsupported.

`model_copy(update=None, deep=False)`, `copy.copy` and `copy.deepcopy` create new
validated same-type models and do not change source values, extras, metadata or
caches. Canonical update keys and extra policy apply; invalid/unsupported updates
fail, and untouched values cannot drift. A frozen source may produce a new valid
updated model; its source remains frozen and unchanged. Immutable scalar leaves
may be shared by identity, but storage/metadata and future mutations are independent.
Preserve existing stronger detachment for supported nested values even with
`deep=False`.

Deprecated `copy` warns and delegates supported update/deep arguments to validated
copy; non-None include/exclude is rejected. `model_construct`, deprecated
`construct` and pickle remain disabled. Audit inherited parse/validation/JSON/
schema conveniences: retain those already routing through supported validation or
serialization, and explicitly reject any confirmed unchecked path. Do not add a
dict-style `copy`, `fromkeys`, binary `|`/reverse `|`, or new parsing convenience.
Direct invocation of base-class implementations/private storage is not supported.

### Serialization and compatibility

Preserve `model_dump`, `model_dump_json`, `model_json_schema` and TypeAdapter
behavior for the scalar envelope: aliases, exclusion, unset/default/None filters,
validation/serialization schema modes, field/model serializers and serialization
context. Field exclusion affects serialized output, not mapping membership.
A model serializer may return a non-object without changing the mapping surface.
No `_pd_*`, guard or coordinator metadata may appear in dumps, schemas or repr.
Use BaseModel controls only for behavior intended to match.

Keep Python `>=3.11`, advertised Python 3.11–3.14, the existing OS matrix, MIT and
exact `pydantic==2.13.4`. This phase neither broadens a Pydantic range nor adds an
independent pydantic-core constraint. Pydantic and its already-required transitive
dependencies remain sufficient for the bare consumer; FastAPI/HTTP/type/build
tooling stay development/integration dependencies.

The only planned externally visible correction is non-string `pop` rejection;
record any further necessary in-scope bug correction with a regression test and
explicit migration impact rather than silently redefining support. No persisted
format or data migration is required. Updates are source/API migrations only.

## Invariants, security and reliability

I1–I5 and I8 from [mutation semantics](mutation-semantics.md#invariants) apply to
every scalar transition. I6/I7 remain mandatory for the inherited nested baseline;
they are not newly redesigned or relaxed in this phase.

- Successful construction/commit satisfies the supported schema and validators.
- Attribute/mapping reads observe one state; every declared field remains present.
- Failure preserves values, extra order, explicit metadata, schema caches, computed caches and existing owned handles; a subsequent valid operation must succeed.
- A batch commits once or not at all; callbacks see previously committed live state during staging/validation/preparation.
- Snapshot/validation/preparation may run trusted user code; prepared commit/restoration does not invoke validators, serializers, descriptors or user comparison/hash callbacks.
- Same-root guard covers input callbacks, validation, preparation, copy and cleanup; failure cannot leave it busy. Other independent roots are not globally locked.
- Unsupported final validator output cannot escape through construction, mutation or copy. No raw mutable fallback or bypass is introduced.
- Serialization is observational, not a state copy or authorization mechanism.

This is trusted-schema validation, not authentication, authorization or containment
of hostile Python. Preserve supported error redaction settings and avoid adding
raw live state to diagnostic strings; Pydantic error details can still contain
input and applications control disclosure. `Field(exclude=True)` does not hide a
field from mapping readers. No new logging, network calls, persistence or secrets
are needed. Fully consumed iterables must be finite and application-bounded;
there is no truncation, timeout or new size/depth limit.

Atomicity is operation-level in supported single-threaded use, not thread safety.
No async API, cancellation protocol or shared-writer lock is introduced. Synchronous
exceptions, including injected `BaseException` at commit boundaries, must restore
state and release the guard; a process kill/power loss is outside this contract.

## Acceptance criteria and verification matrix

Every criterion describes release-observable behavior or an executable static/
artifact gate. Existing tests may prove a criterion; add missing cells, not a
second implementation-specific oracle. Required behavior cannot be skipped or
marked expected-failure. Baseline defects outside this boundary are not automatic
requirements.

| ID | Required observable outcome | Preferred proof / existing anchor |
| --- | --- | --- |
| AC-001 | All listed scalar leaves and supported scalar annotation forms construct through their applicable Python/JSON/strings modes; constraints and strict/coercing behavior match the pinned schema. | Unit/contract, T3/T6; leaf/mode table, BaseModel controls, new scalar fixtures. |
| AC-002 | Unsupported input or validator-produced values fail before construction/copy returns or mutation commits; existing supported mutable inputs still work with guards. | Contract/compatibility; `test_phase02_contract.py`, `test_hash_ingress.py`, broad scalar/extra output cases. |
| AC-003 | Models are BaseModel/Mapping/MutableMapping instances; attribute/item values agree, canonical/default/excluded keys and extra order follow the specified rules. | Unit/contract, T2; `test_prototype.py`, new scalar read matrix. |
| AC-004 | Missing/non-string reads, membership, get defaults, empty truth/length, live views, dict/unpack/pattern consumers behave as specified without invoking serializers. | Unit/integration, T2/T9; mapping-only reader assertions and scalar views. |
| AC-005 | Key iterators invalidate on committed ordered-key changes, including before first next; value-only/failure/no-op changes do not invalidate, and exhausted iterators remain exhausted. | Contract/property; scalar iterator/view transition tests, D26 controls. |
| AC-006 | Protected canonical/extra/property/computed names and ambiguous aliases fail; safe canonical fields with method-like aliases still validate/serialize and use only canonical mapping addresses. | Unit/compatibility; `test_inventory.py`, namespace/alias fixtures. |
| AC-007 | Single item and attribute writes return None and commit equivalent validated state; invalid values and model-validator failures preserve values/order/metadata/caches. | Unit/differential, T3/T6; Bounds control and scalar parameter matrix. |
| AC-008 | Mapping/pair/keyword/self updates and in-place union resolve duplicate precedence correctly; coupled changes commit atomically, update returns None and union retains identity. | Contract/integration, T4; Bounds and mapping-only writer consumer. |
| AC-009 | Late input exceptions and malformed pairs commit nothing and preserve Python exception distinctions; non-string mutating names, including pop fallback, raise TypeError before policy/validation. | Unit/contract, T4/T5; exact pop regression and malformed/key precedence cases. |
| AC-010 | Existing-key setdefault ignores its unused default without validation; absent allowed insertion returns the coerced stored scalar; forbidden/ignored unknown writes fail. | Unit/contract, T3/T5; typed/untyped extra fixtures. |
| AC-011 | Declared fields cannot be deleted/popped/cleared; extra removal obeys last-key order, exact missing fallback and empty errors; validator-rejected fieldless clear rolls back. | Unit/contract, T5; destructive required/default/nullable/fieldless matrix. |
| AC-012 | Reset only reevaluates selected defaults once per selected field; deduplication, field-order factories, required/extra/missing errors and factory failure follow the contract. | Unit/differential, T5/T6; data-dependent reset fixture, counter/failing factories. |
| AC-013 | Frozen fields/models reject requested writes, equal scalar writes and mixed batches; specified missing/existing/empty no-ops retain their normal behavior. | Unit/compatibility, T3–T6; every applicable mutator × freeze/key-existence matrix. |
| AC-014 | Fields-set and extra snapshots cannot mutate model state; explicit assignment/reset/removal metadata and exclude_unset output follow the specified transitions without marking omitted defaults. | Unit/differential, T6; metadata transition table and snapshot-edit tests. |
| AC-015 | Canonical-safe validators work without untouched drift; unsupported observable drift raises its stable diagnostic; programming exceptions propagate, and mutation/copy do not retain construction context. | Contract/differential, T6; non-idempotent control, context and validator-mode fixtures. |
| AC-016 | Reentrant mutation/copy from staging or validators fails before live change; all pre-commit and injected commit-swap failures preserve complete state and allow a subsequent valid write. | Contract/fault, T4/T6; `test_transaction_remediation.py`, scalar failure/recovery fixture. |
| AC-017 | Successful scalar commits invalidate supported computed caches; failed/empty operations preserve caches and views of prior state. | Unit/contract, T6; cached computed-field fixture with failure/no-op controls. |
| AC-018 | Every supported copy is a new validated same-type independent model; invalid updates/drift fail, metadata is preserved/updated, and valid frozen-source copy updates leave the source unchanged. | Unit/compatibility, T6; copy API × scalar/extra/frozen/update matrix. |
| AC-019 | Deprecated copy emits its warning and rejects partial copies; construct/deprecated construct/pickle remain disabled; inherited supported parse/dump/schema paths do not bypass validated state. | Contract/compatibility, T6; public inherited-method inventory and disabled-path tests. |
| AC-020 | Python/JSON/strings/TypeAdapter and existing-model validation honor applicable flags/context, detach sources before callbacks and preserve configured ongoing extra policy. | Contract/differential, T6; `test_compat_remediation.py`, existing public-entry remediation fixtures. |
| AC-021 | Scalar dumps/JSON/schema preserve aliases, exclusion, unset/default/None filtering, serializers and context; no private engine state leaks and mapping keys are unchanged. | Contract/integration, G1/G2; BaseModel controls and installed scalar consumer. |
| AC-022 | Equality remains model equality rather than dict equality, mutable instances are unhashable and supported frozen scalar hashing matches Pydantic controls. | Compatibility/unit, T2/T6; equality/hash fixtures including allowed extras. |
| AC-023 | Strict positive fixtures retain precise attributes, object mapping values, typed views and Self copies; independent negative diagnostics match exact rule/location and installed public completeness is 100%. | Static/contract, T10; existing typing helper and both installed-wheel paths. |
| AC-024 | Direct and sdist-rebuilt wheels install outside the checkout with scalar readers/writers/default/copy workflows passing; name/version/license/py.typed and exact dependency policy are verified with no source injection or development-tool runtime requirement. | Artifact/integration, T1/G5; extend `tools/qualify_package.py`, retain its nested/HTTP checks. |
| AC-025 | All advertised Python/OS lanes pass existing gates and scalar additions; qualification records exact source, interpreter and resolved upstream versions, commands and artifact hashes. | Compatibility/static/artifact, G4; existing eight runtime and two artifact lanes with candidate evidence. |
| AC-026 | At least 100 generated scalar sequences of 100 steps each agree with an independent transition oracle for values/key order/metadata, and every rejected operation leaves state unchanged. | Property/stateful, T3–T6; scalar bounds/default/extra machine; report settings/replay information. |
| AC-027 | The full prior Phase 0.2 regression suite still passes; no supported nested annotation, guarded mutation, ownership/copy behavior, iterator policy or prior fix is removed to meet the scalar boundary. | Compatibility/integration; all `tests/`, protected re-review tests and existing artifact consumers. |
| AC-028 | A runnable installed scalar library-config example and updated API/error/support/migration docs agree with tested behavior; docs links/examples pass and scalar milestone claims do not imply arbitrary nested lifetime support or completed publication. | Integration/manual/static, T12; scalar example, docs checker and AC-linked evidence review. |

## Implementation phases — recommended execution

Internal filenames below are recommendations, not new public APIs. Keep a bounded
change; an AC already demonstrated by a suitable test does not require a rewrite.

### P1 — Coverage inventory and scalar baseline

**Goal:** map T2–T6/T10 and AC-001–028 to executable proof before making changes.
**Modules:** tests, existing core/adapter APIs and qualification/typing helpers.
**Required work:** introduce a scalar-only Bounds/defaults/extras fixture set and
an AC coverage inventory with existing/new test node IDs; identify non-applicable
matrix cells explicitly. Preserve all old/protected tests and historical evidence.
**Tests:** snapshot values/order/fields-set/extras/cache identity, not just dumps;
use BaseModel controls only for intended compatibility. Capture baseline failure
of the non-string pop contract and make it a passing required regression in P3.
**Docs/config:** record the current support matrix and this phase's scalar boundary.
**Dependencies:** completed Phase 0.2, no external participant prerequisite.

### P2 — Reads and namespace qualification (W06)

**Goal:** prove the canonical scalar mapping interface and namespace policy.
**Modules:** `_core.py` read/name methods; scalar read/alias tests and type fixtures.
**Required behavior:** AC-003–006, AC-022 and read portions of AC-023; no serializer
coupling, alternate alias keys or concrete-dict promises.
**Tests:** default/excluded/extra/fieldless cases; before-first-next/exhausted
iterators; values-only replacement; safe method-like aliases and protected names;
Mapping/MutableMapping consumers, unpack and pattern matching.
**Docs:** API namespace/read examples and deliberate equality/iteration divergence.
**Dependencies:** P1.

### P3 — Scalar transaction/policy completion (W07)

**Goal:** close scalar mutation matrix gaps through the existing engine.
**Modules:** `_core.py` mutators/transaction/preparation; adapter only if necessary.
**Required behavior:** AC-007–017 and scalar input/output checks in AC-001/002.
Correct non-string pop handling at the public mutator boundary without changing
read/fallback semantics. Do not implement bulk operations as sequential assignment.
**Tests:** all applicable mutator × required/default/nullable/typed-extra/untyped-
extra/forbid/ignore/frozen cells; duplicate/keyword precedence; malformed/late input;
reset factory order/failure; metadata/cache failure/no-op checks; reentrancy before
input callbacks; all scalar prepared-swap restoration points plus recovery.
**Docs:** mutator/error table, stable codes, explicit non-string pop correction.
**Dependencies:** P1/P2; preserve previously passing nested tests after each change.

### P4 — Lifecycle, copy and static compatibility

**Goal:** prove scalar lifecycle and safe copies without widening hook support.
**Modules:** core validation/copy/schema hooks, adapter validator caches, typing
fixtures/helper and scalar lifecycle/serializer tests.
**Required behavior:** AC-015/018–023; retained supported entry-point signatures,
trusted-path rejection, source isolation, frozen copy semantics and raw-state
serialization separation.
**Tests:** Python/JSON/strings/TypeAdapter paths, explicit alias flags/context,
forward-reference rebuild/scalar generics; copy/copy.deepcopy/deprecated matrix;
callback-produced unsupported output; cache invalidation and disabled configuration.
Negative fixtures continue verifying their actual diagnostics, not zero analyzed files.
**Docs:** supported hooks/validators, copy/trusted divergence, metadata migration.
**Dependencies:** P3.

### P5 — Installed consumers and robustness qualification

**Goal:** verify deployable scalar behavior and record reproducible evidence.
**Modules:** `tools/qualify_package.py`, scalar state machine, one public scalar
example (recommended `examples/library_config.py`), existing CI wiring as needed.
**Required behavior:** AC-024–028; preserve existing nested bare-consumer and HTTP
checks. Run the scalar example with assertions against both wheel paths, with
`PYTHONPATH` cleared, outside the checkout, using no private APIs. Include a
mapping-only reader/writer, coupled-update success/failure, reset, metadata and copy.
**Tests:** 100 × 100 scalar stateful profile, full production regression, installed
positive/negative typing/completeness, all existing runtime/artifact matrix lanes.
Any helper include/exclude changes must keep `check_typing.py`'s source-inventory
expectations consistent; do not reduce strict coverage to fit a new file.
**Docs/config:** fresh `docs/research/phase-0.3-findings.md` and machine-readable
results only after execution, with AC-to-test/lane proof, exact provenance,
versions/commands, artifacts/hashes, failures and limitations. Reuse old reports
as history, never overwrite them with new measurements or invented passing status.
**Dependencies:** P4; full passing matrix required before declaring qualification.

W07 should also collect a scalar cost baseline without a timing pass/fail ceiling:
five/50/500-field records; construction, key/attribute reads, dict conversion,
single write, coupled batch, rejected batch, reset and copy. Record three runs,
environment, raw samples, median/p95 and separately traced peak allocations using
the existing measurement approach or a separate scalar harness. Do not change
historical benchmark fixtures/baseline identifiers just to repurpose their report.
Numeric beta budgets and optimizations remain W10 follow-up, not new 0.3 blockers.

### P6 — Contract reconciliation and handoff

**Goal:** make support claims match evidence and leave a release-ready change,
without publishing it.
**Modules:** README, roadmap/backlog, API/mutation/testing/compatibility/typing,
decisions, release/support docs and Unreleased changelog.
**Required behavior:** AC-025/027/028; distinguish previously shipped nested support,
new scalar qualification and future 0.4 work. Record G1/G2 scalar proof, G4 exact
matrix and G5 retained license/name/metadata policy. No new license-selection,
package-name acquisition or private-reporting configuration task is invented.
**Verification:** all required gates and evidence audit below; no asserted new
passing artifact/CI result without its actual run. Prepare source/API migration
notes for bug corrections, especially pop's key behavior.
**Dependencies:** P5. Version/tag/publication remain a separately authorized run.

## Risks and explicit non-scope

- Full-root revalidation is intentionally conservative and can rerun callbacks.
  Retain validator restrictions/drift checks; do not optimize by field-only validation.
- Error precedence can be accidentally changed while fixing pop. Add mixed
  non-string/missing/frozen/invalid-default tests and preserve unused fallbacks.
- Scalar edits still pass through graph-aware preparation. Keep existing ownership,
  serializer, retained-handle and rollback regressions mandatory.
- Locally stale distribution metadata can create misleading evidence. Qualify the
  source and each new artifact separately and verify installed origin/version.
- Private Pydantic APIs remain version-sensitive. Keep the exact pin/adapter;
  no neighboring-minor support is inferred from a scalar test passing.
- CI/upstream dependency resolution may differ by platform. Record actual compatible
  resolved stacks, not one local environment presented as every lane.

Explicit non-scope: engine rewrite/module-splitting project; new nested types,
guards or ownership semantics; arbitrary BaseModel/enum/secret/custom-timezone
support; framework plugins; broader dependency or interpreter support; binary union,
dict-copy/fromkeys/conversion APIs; custom hook support; async validation/thread
safety; persistence/pickle/migrations; reactivity; generated typing/checker plugins;
performance optimization and numeric beta ceilings; all three beta journeys;
external participants/trials; supply-chain workflow redesign; publication.

## Known follow-up candidates

Open issues were searched through GitHub during planning; no new unrelated
runtime defect was confirmed that needs a new issue.

- [Issue #2](https://github.com/eddiethedean/pydandict/issues/2): investigate
  repeated root-after-validator invocation on self-recursive schemas. Pre-existing
  nested callback-count work, not scalar qualification or a new exactly-once promise.
- [Issue #1](https://github.com/eddiethedean/pydandict/issues/1) remains open, but
  its security-policy/private-route requirements appear implemented in the current
  source and the private-reporting API is enabled. Maintainer can reconcile issue
  status separately; do not duplicate it or make issue closure a 0.3 gate.
- General stale status vocabulary elsewhere in the planning corpus is documentation
  debt. Correct statements touched by 0.3 support claims, not the entire repository.
- W08–W12 retain broader ownership/ecosystem, numeric performance budgets, remaining
  beta journeys and exact-candidate release work.

The confirmed pop defect is implementation work under AC-009, not a follow-up.
The local installed-version mismatch is environment setup, not a package issue.

## Definition of done

This change is done when all Phase 0.3 ACs have executable evidence, required
compatibility is preserved, no substantive regression/blocker attributable to this
change remains, and affected docs agree with observed behavior. Run these existing
source gates, plus the scalar release profile and installed consumers defined above:

```sh
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests -q
python -m ruff check src tests tools/check_typing.py tools/qualify_package.py tools/benchmark.py
python -m ruff format --check src tests tools/check_typing.py tools/qualify_package.py tools/benchmark.py
PYTHONPATH=src python tools/check_typing.py
PYTHONPATH=src python -m pyright --verifytypes pydandict --ignoreexternal
python tools/check_docs.py
python tools/qualify_package.py
```

The complete advertised CI matrix and AC-linked candidate evidence are required;
a local run is not all-platform proof. Independently confirmed pre-existing
out-of-scope gate failures must be recorded with proof, not silently treated as
passing. The repository need not be globally defect-free. Implementation completion
does not itself mean version 0.3.0 was tagged or published.

### Final planning verification note

The plan is grounded in source inspection and the planning checks listed above;
Phase 0.3's new contracts and artifact/matrix acceptance work remain unimplemented.
After adding this plan and its navigation links, documentation verification passed
for 38 Markdown files, 251 local links and eight Python examples with zero errors;
`git diff --check` passed. Only planning/navigation Markdown files were changed;
production code, tests, package metadata, workflows and historical evidence were
not modified. The 151-test run proves the inspected baseline, not completion of
the new acceptance criteria.

READY FOR IMPLEMENTATION
