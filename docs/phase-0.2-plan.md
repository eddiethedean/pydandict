# Phase 0.2 — Architecture and implementation contract

Status: **IMPLEMENTED; INDEPENDENT REVIEW PASS; RELEASED 2026-09-14**. This approved contract remains
the Phase 0.2 scope authority; the [completed review](reviews/phase-0.2-rereview-6.md)
records its verification. Version 0.2.0 is published as
[PydanDict 0.2.0](https://pypi.org/project/pydandict/0.2.0/), the current public release.

This is the authoritative implementation and review boundary for Phase 0.2.
It resolves the Phase 0.2 questions in the [roadmap](../ROADMAP.md#02--prototype-hardening-and-contract-finalization)
and [work packages](implementation-plan.md#questions-carried-into-phase-02).
Where older proposed v1 targets differ, the requirements here govern this change;
the implementation must update the affected API, ownership, typing and compatibility
documentation. Broader v1 goals remain future work. D18 (no external participants)
and D22 (build on Phase 0.1) remain unchanged.

## Architecture summary

Keep the existing engine: a genuine `BaseModel`/`MutableMapping[str, object]`,
detached finite-tree inputs, full-root canonical Pydantic validation, private
mutable ABC guards, identity reconciliation, and prepared storage swaps with
rollback. Do not substitute sequential assignment, serialized transaction input,
a second writable store, or incremental validation.

Phase 0.2 makes this conservative engine auditable and its supported contract
explicit. It requires honest mutable annotations, structured rejection diagnostics,
complete production-source strict typing, actual negative typing verification,
adapter boundary tests, installed production-artifact consumers, and a measured
large/deep baseline. It does not require faster mutations or broader dependencies.

Recommended responsibility split:

| Module | Responsibility |
| --- | --- |
| `src/pydandict/__init__.py` | Preserve the sole public export, `DictModel`, and `py.typed` packaging. |
| `src/pydandict/_core.py` | Public model/mapping methods, canonical key policy, configuration checks and delegation from Pydantic extension hooks. |
| `src/pydandict/_compat.py` (new) | Pydantic storage access/allocation, fields-set restoration, complete-schema inspection, canonical/alias validator caches, serializer delegation and storage swaps. |
| `src/pydandict/_ownership.py` (new) | Closed value classification, detached snapshots, fingerprints, origin tracking, reconciliation and detached return preparation. |
| `src/pydandict/_transaction.py` (new) | Same-root guard, operation staging, validation, preparation, commit/rollback and recovery. |
| `src/pydandict/_containers.py` | Typed private sequence/mapping/set handles; every mutator delegates to the root coordinator. |

These filenames are recommended implementation, not additional public APIs. An
implementer may merge a small helper or add a private protocol/error module if the
boundaries remain clear. All raw Pydantic storage access, core-schema manipulation
and compiled-validator cache ownership must remain behind one compatibility
boundary. Public class metadata such as `model_fields` may be used by key policy;
Pydantic extension-hook definitions may remain on `DictModel` and delegate inward.
Use typed internal protocols to avoid model/container import cycles.

### Repository ground truth

Inspected base: commit `07fec9b7eafef5b00befe9fa24ccd012ce0232a1` on `main`.
The working tree was clean before this planning change.

| Surface | Existing implementation / evidence |
| --- | --- |
| Production package | `src/pydandict/_core.py` combines adapter, graph, transaction and public API responsibilities; `_containers.py` contains private ABC guards. |
| Public interface | Only `DictModel` is exported; key iteration, all mapping mutators, `reset`, validated copies and Pydantic validation entry points already exist. |
| Runtime suite | `tests/test_prototype.py`, `test_inventory.py` and `test_stateful.py` run against `pydandict`; 87 tests pass locally. |
| Ownership baseline | Inputs detach, retained handles survive reorder, removed handles become stale, copies detach, ancestor validation/freeze is enforced, and commit fault injection exists. |
| Known typing gap | Default Pyright analyzes two files and reports zero errors. Explicit strict analysis of `_core.py` and `_containers.py` reports 341 errors. |
| Known negative-fixture gap | `tests/typing_negative.py` is excluded; the current CI command exits successfully with **zero files analyzed**. Its four expected errors are not verified by CI. |
| Artifact evidence | `prototypes/run_checks.py` builds and tests `pydandict_prototype`, not the root production distribution. CI builds production artifacts for release, but does not run their isolated consumers. |
| Packaging | Version `0.1.0`, MIT, Python `>=3.11`, classifiers 3.11–3.14, sole direct runtime dependency `pydantic==2.13.4`. |
| Development controls | FastAPI `0.141.1`, httpx `0.28.1`, Pyright `1.1.411`; other development tools are currently unpinned. |
| CI / release | Every push and PR calls `check.yml`; current checks use Ubuntu/Python 3.11 only. Tag releases call the same workflow with package preflight, build distributions, then use PyPI Trusted Publishing. |
| Persistence | None. Pickle and trusted construction are already rejected; no database or migration infrastructure exists. |

Local inspection used CPython 3.11.14 on macOS, Pydantic 2.13.4,
pydantic-core 2.46.4, FastAPI 0.141.1, Starlette 0.48.0, httpx 0.28.1,
Pyright 1.1.411, pytest 9.1.1, Hypothesis 6.151.9 and Ruff 0.15.6.
The recorded prototype has a different Starlette version; keep each environment's
resolved versions distinct rather than silently rewriting historical evidence.

Reproduced commands:

```sh
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests -q
python tools/check_docs.py
PYTHONPATH=src python -m pyright --outputjson
PYTHONPATH=src python -m pyright src/pydandict/_core.py src/pydandict/_containers.py --outputjson
PYTHONPATH=src python -m pyright tests/typing_negative.py --outputjson
```

Results: 87 runtime tests passed; 24 Markdown files, 164 local links and six Python
examples passed documentation validation. The three typing runs respectively
analyzed 2/2/0 files and reported 0/341/0 errors. The explicit internal failures
are in scope, not an exemption from Phase 0.2. An initial runtime command without
installation or `PYTHONPATH=src` failed import collection; the corrected command
passed, so that was an environment setup failure, not a package defect.
An independent copy of the negative fixture, using a strict configuration with
no exclusions, analyzed one file and produced exactly its four expected
rule/location errors. This confirms that the CI problem is the exclusion, not
obsolete expectations. The ABC migration example below was also executed against
the baseline and produced the expected serialized payload.

Relevant contracts inspected: [API](api.md), [mutation invariants](mutation-semantics.md),
[ownership](nested-values.md), [architecture](architecture.md), [typing](typing.md),
[compatibility](compatibility.md), [testing](testing.md), [quality bar](quality-bar.md),
[decisions D07–D22](decisions/README.md), examples and prototype consumers.

## Change boundary

**Problem.** The released Phase 0.1 engine has demonstrated a useful conservative
envelope, but several choices still read as experimental, concrete mutable field
annotations promise runtime identities the guards cannot provide, and current
CI leaves private-source typing, negative diagnostics, production consumers and
advertised runtime minors unqualified.

**Desired outcome.** Model authors can tell which annotations, hooks and operations
are supported; ordinary supported mutations remain atomic and continuously
validated; unsupported cases fail without corrupting live state; the private
implementation passes strict Pyright; and automated checks qualify the production
package on a finite, declared matrix. Phase 0.3 can extend this engine without
reopening these architectural choices.

**In scope:** finalizing D07–D17/D19–D21 for this envelope; container annotation and
value safety policy; identity/writeback, iterator, copy and removal semantics;
deterministic diagnostics; same-root recovery and callback boundaries; adapter
isolation/cache invalidation; targeted adversarial/stateful tests; production
artifact/typing/HTTP consumers; runtime CI matrix; measured large/deep workloads;
relevant documentation and migration instructions.

**Touched surface:** production private modules and public-method annotations;
`tests/` and new contract/compatibility tests; `pyproject.toml` typing configuration;
`check.yml` and only necessary reusable-workflow integration; new standard-library
qualification/typing/benchmark helpers under `tools/`; README, roadmap, changelog,
API/mutation/ownership/typing/compatibility/testing docs and decision statuses;
new Phase 0.2 evidence under `docs/research/`.

The prototype implementation, its recorded results and upstream probes remain
historical controls. Port useful cases to production fixtures without rewriting
the original evidence or making prototype imports part of production qualification.
There is no persisted-state migration; the only required migration is source
annotation/API guidance from the alpha baseline.

## Public contract — required behavior

### APIs, names, defaults and returns

Preserve `from pydandict import DictModel`, genuine nominal model/mapping identity,
canonical field-name keys, field order followed by extra insertion order, and
shared attribute/key state. Mapping reads return `object`; attributes retain
their declared types. `get` defaults, live typed views, `Self` copies and `|=`,
and `None`-returning `update`/`reset` remain as documented in the API.

Preserve D07–D15 and D19 within this envelope: all declared fields remain present;
only allowed extras may be deleted/popped; `reset` restores validated defaults;
ignore-input configuration still rejects unknown mutation keys; aliases remain
input/output boundaries; equality remains model equality rather than dictionary
equality; mutable models are unhashable. Frozen models with fully immutable,
hashable supported state retain the Pydantic-compatible hash path; frozen mutable
state does not become hashable merely because it is frozen.

No new exported error class, collection class, public transaction object, positional
mapping constructor, checker plugin or validation-off option is introduced.

### Annotation and owned-value envelope

The Phase 0.2 annotation policy deliberately narrows the alpha contract:

| Annotation / value | Required treatment |
| --- | --- |
| `MutableSequence[T]`, `MutableMapping[K, V]`, `MutableSet[T]` | Supported mutable field annotations, including nested occurrences; runtime values satisfy those ABCs and retain validated generic element/value types. Ordinary list/dict/set inputs remain accepted according to Pydantic coercion and strictness. |
| `list[T]`, `dict[K, V]`, `set[T]`, their bare forms and equivalent typing aliases | Reject as declared model-field annotations at schema completion, including nested/union/generic occurrences. Return a diagnostic identifying the field and corresponding ABC replacement. Do not ship a stub that lies about concrete identity. |
| Safe scalar/value annotations, `Literal`, nullable unions, `Annotated`, tuple/frozenset aggregates and nested `DictModel` | Preserve Pydantic schemas and validation within the owned-value rules below. Resolve aliases/forward references and inspect specialized generics when their schema becomes complete. |
| `Any`, `object`, untyped extras | Allowed broad schema; inspect the actual validated value and own or reject it. No arbitrary-object exemption. |
| Pydantic typed-extra declaration `__pydantic_extra__: dict[str, V]` | The outer dict is Pydantic metadata, not a public model field, and is exempt from the concrete-annotation ban. Audit `V` recursively under the same field-value policy. Metadata snapshots retain their usual plain-dict public type. |
| Other collection annotations, arbitrary object types, ordinary `BaseModel` and custom ownership/schema adapters | Outside this envelope. Reject a declared unsupported value annotation when identifiable, or reject its resulting unsafe value before it escapes. No new type adapter/plugin interface. |

ClassVars, configuration, validator/serializer parameter annotations and local
input variables are not model fields and are not subject to the field-annotation
ban. Serializers continue to receive raw Pydantic snapshot values, so their
parameters may correctly use concrete container types.

Supported leaves remain exact `None`, `bool`, `int`, `float`, `str`, `bytes`,
`Decimal`, `date`, `datetime`, `time`, `timedelta`, and `UUID` types. Do not add
enums, scalar subclasses, secret wrappers or arbitrary immutable-looking classes
in this change. `datetime`/`time` must have no timezone or an exact standard-library
`datetime.timezone`; reject custom timezone payloads whose mutable callbacks defeat
the closed-value assumption. Adding other timezone types is later support work.

Supported graphs are finite lists/dicts/sets, owned ABC guards, tuples/frozensets,
and nested `DictModel` values. Repeated mutable occurrences detach into independent
trees; true cycles are rejected. Dictionary keys and set/frozenset members must be
recursively immutable, hashable combinations of the supported leaves and
tuples/frozensets, not models, guards or user-defined hash/equality objects.
The guard installation must check final validator output as well as external input.

Deferred Pydantic forward-reference completion is permitted. An unsupported
annotation must fail before a complete schema validates and returns an instance,
not create a usable but unsound model first. Rebuilding a schema before instance
use must invalidate class-local compiled variants. Changing schema/configuration
after instances have escaped remains unsupported.
Generic class declarations remain possible, but public instance construction
requires fully explicit specialization, such as `Box[MutableSequence[int]]` or
`Box[int]`. Reject constructing a class with unbound model type parameters and
explain how to specialize it; otherwise constructor type inference can silently
promise `Box[list[int]]` while the runtime payload is a guard. Broad generic use
may explicitly specialize with `Any` and remains subject to actual-value ownership.

Required migration example:

```python
from collections.abc import MutableMapping, MutableSequence, MutableSet
from pydantic import Field
from pydandict import DictModel


class Settings(DictModel):
    retries: MutableSequence[int] = Field(default_factory=list)
    groups: MutableMapping[str, MutableSequence[int]] = Field(default_factory=dict)
    flags: MutableSet[str] = Field(default_factory=set)


settings = Settings(retries=[1], groups={"primary": [2]}, flags={"ready"})
print(dict(settings))
```

Observed output:

```text
{'retries': [1], 'groups': {'primary': [2]}, 'flags': {'ready'}}
```

This is an intentional alpha compatibility break; document it prominently. Values
and serialized payloads remain list/dict/set-shaped. APIs requiring concrete
built-ins should consume an explicit suitable serialized payload or shallow
conversion, recognizing that shallow conversion retains guarded descendants.
Static consumers receive the methods defined by the chosen ABC, not every method
of a built-in container. Extra guard conveniences such as sequence `sort` are
runtime conveniences; typed code can assign `sorted(model.retries)` when it needs
sorting through the declared ABC contract. Do not add a public collection family
to hide that distinction.
Arbitrary-object `from_attributes=True` construction is not added: the existing
closed-input ownership envelope rejects such objects. Keep the Pydantic-compatible
method parameter without advertising support for arbitrary attribute sources.

### Validators, hooks, configuration and extensions

| Surface | Required Phase 0.2 contract |
| --- | --- |
| Field/model before, after, plain and wrap validators; annotated validator forms | Supported only when deterministic, safe to rerun on canonical Python state, and schema-sound. Normalization is idempotent on untouched state; retained mutable topology is preserved. Model-after validators return their candidate instance. Do not manually invoke decorators or promise to infer arbitrary validator semantics. |
| Changed/replaced inputs | May undergo normal Pydantic coercion/normalization. This does not make a non-idempotent validator supported for unrelated later writes. |
| Observable unsupported drift/topology | Reject before commit; preserve live state and return the specific library diagnostic. Pure external side effects and arbitrary trusted-schema unsoundness cannot be detected or reversed. |
| Construction modes/context | Keep constructor, `model_validate`, JSON/strings validation, TypeAdapter and nested construction. Pass supplied strictness, alias flags, extra policy and context through the public boundary according to the pinned Pydantic behavior. |
| Mutation/copy context | Revalidate canonical Python state with `context=None`; never retain request context or change mutation mode based on construction mode. Validators requiring request context for ongoing state invariants are unsupported. |
| Required configuration | `validate_assignment=True`, model/field default validation, `revalidate_instances='always'`; attempts to disable these fail class setup. Extra policy remains configurable; reject conflicting one-off stored-extra results. |
| Private attributes, custom initialization/finalization, `model_post_init`, writable properties | Preserve explicit rejection. Read-only/computed properties and supported cached computed fields remain usable and excluded from mapping keys. |
| Trusted/deprecated paths | `model_construct`, deprecated construct and pickle remain rejected. Deprecated copy warns, validates supported arguments, and rejects partial include/exclude copies. |
| Safety-critical overrides and hostile callbacks | Outside the contract. Ordinary field validators/serializers remain trusted extension code; overriding bridge, ownership or schema safety machinery does not receive a safety guarantee. |

### Transactions, identity and iterator lifecycle

Acquire the same-root busy guard before consuming operation iterables or running
callbacks. Stage the complete operation on detached raw state, validate the root,
prepare ownership, metadata, return values and undo information, then swap storage.
No retry is allowed after a callback or default factory fails. All failure paths
release the guard and reset temporary ContextVars.

The unchanged root retains its identity. Saved model/container handles follow
the same retained node across in-place edits, reorder and unrelated writes.
Replacement/removal or union-branch replacement makes old subtree handles stale
for public reads and writes. Adoption from another root always detaches.

Single-slot assignment of the exact currently stored owned guard or `DictModel`
is an explicit identity no-op after liveness, existence and freeze/policy checks.
This applies to model attributes/keys and owned sequence/mapping slots. Manual
identity assignment and augmented-assignment writeback have identical semantics;
the implementation must not inspect bytecode to distinguish them. They do not
rerun validators, change fields-set/caches, or invalidate iterators. A frozen
write request still fails, even when the value is identical. Equal scalars are
ordinary writes. `update(field=current_handle)` is an explicit replacement
transaction and does not receive the single-slot identity shortcut.

Augmented assignments through supported slots commit one root transaction; the
subsequent same-handle writeback cannot create a duplicate validation or post-commit
failure. Bulk update materializes mappings/pairs, resolves duplicates and keyword
precedence, and validates once as a complete operation. Empty model update/reset
and existing-key setdefault do not run validators. Container mutator calls such as
add-existing, discard-missing, sort-already-sorted and multiply-by-one still take
the ordinary container transaction path unless they are a specified identity
writeback or existing-key setdefault.

Supported augmented-assignment slots are canonical model fields/extras and owned
sequence/mapping entries. Tuple indices and read-only/computed properties are not
assignable slots: Python may run an in-place child operation before rejecting the
subsequent slot assignment. Use `model.pair[0].append(value)` rather than
`model.pair[0] += values`. Expression-level rollback for such unsupported syntax
is not promised. One root validation pass also does not promise that Pydantic
internally invokes each nested validator exactly once.

Model key iterators invalidate only when that model's ordered key structure
changes. Owned container iterators, including reverse and view iterators, are
conservative: **any committed root transaction invalidates them**, even a scalar
write or value overwrite elsewhere in the root. Failed transactions and specified
identity/no-op paths invalidate neither. Capture the version when the iterator
is created, not on its first `next()`. Once exhausted, an iterator stays exhausted.
Views remain live and can create fresh iterators after a commit. Do not promise
multi-read snapshot consistency or thread safety.

### Copies, removals, metadata and serialization

Successful pop/popitem returns represent pre-removal values in a detached usable
graph: plain mutable containers and independently owned nested `DictModel` roots.
Prepare that graph before committing removal. Old borrowed handles become stale;
failure during result preparation changes neither state nor handles.

`model_copy`, supported deprecated copy, `copy.copy(model)` and `copy.deepcopy(model)`
produce independently validated ownership roots even with `deep=False`; update
keys are canonical and validated. Copy with an update may create a new value for a
frozen source without modifying it. `copy.deepcopy(guard)` returns a detached
usable graph, including fully installed nested models. Never return an internal
blank candidate as a purported public model.

Shallow `dict(model)`, container copy, slice and non-mutating collection operations
may retain guarded descendants. They must not expose writable raw payloads.
Detached `model_extra` and `model_fields_set` containers preserve metadata safety;
extra snapshot values may remain guarded, just as a shallow mapping copy does.

Preserve explicit-field metadata, ancestor marking on nested writes, reset-name
deduplication, default/factory order, exclusion behavior and invalidation of cached
computed fields. Failure preserves cached objects as well as values and handles.
Retain old storage/cache references through the entire swap sequence; dispose of
them after all swaps while the same-root guard is still active. User callbacks
must not observe a half-committed root through commit-triggered disposal.

Delegate dumps, JSON dumps, schemas and supported framework output to Pydantic via
raw snapshots; do not serialize by iterating mapping items. Preserve alias rules,
exclusions, validation/serialization schema modes, context, computed fields and
custom serializer output shape. Mapping reads never invoke serializers. Snapshot
serializers are trusted observational callbacks: they must not depend on live
model identity or mutate the owning root. No universal standalone guard-encoder
compatibility is promised; direct unsupported JSON encoding must fail instead of
silently returning empty container data.

### Errors and security/reliability boundary

Preserve Python `KeyError`/`AttributeError`, malformed-input `TypeError`/`ValueError`,
Pydantic `ValidationError` details, and validator programming/dependency exceptions.
Do not wrap all failures as validation errors. Library-created validation policy
codes remain `pydandict_field_deletion`, `pydandict_reset_required`, `extra_forbidden`
and the current `frozen_instance` policy code.

For non-validation library diagnostics, retain TypeError/RuntimeError rather than
adding an exported exception type. Give messages these stable leading codes:

| Leading code | Exception / condition |
| --- | --- |
| `pydandict_unsupported_annotation:` | TypeError; incompatible declared value annotation with field path and ABC migration hint where applicable. |
| `pydandict_unsupported_value:` | TypeError; unsafe actual value/key/member/timezone. |
| `pydandict_cycle:` | TypeError; cyclic input or validated graph. |
| `pydandict_canonical_drift:` | TypeError; untouched canonical state changed. |
| `pydandict_topology_change:` | TypeError; a validator unexpectedly changed retained mutable topology. |
| `pydandict_unsupported_configuration:` | TypeError; disabled validation, unsupported hook or inconsistent stored-extra policy. |
| `pydandict_protected_name:` | TypeError; method/private/computed/alias namespace collision. |
| `pydandict_incompatible_pydantic:` | TypeError; unsupported installed Pydantic version or incompatible required adapter structure. |
| `pydandict_trusted_path_disabled:` | TypeError; construct/pickle/partial-copy bypass. |
| `pydandict_stale_handle:` | RuntimeError; stale model/container access. |
| `pydandict_reentrant_transaction:` | RuntimeError; mutation/copy reentry into a busy root. |
| `pydandict_iterator_invalidated:` | RuntimeError; invalidated iterator. |

Suffix wording is explanatory and may change; prefix, exception category and
validation-policy codes are the observable contract. When both drift and topology
checks apply, the first detected check may determine the diagnostic. Never add
raw field values/full snapshots to library messages; preserve Pydantic redaction
settings for its own errors. Keys/field paths and type/version names are sufficient.

Trust schemas, validators, serializers and callers' Python code. Authentication,
authorization, network I/O and persistence are not package responsibilities.
Reflection, raw internal writes, explicit base-method bypass, unsafe deserialization
and hostile safety overrides remain outside scope. External callback effects are
not transactional. Shared threads/tasks need application synchronization; no
async suspension, locking service or cancellation API is added. Finite large/deep
inputs must either succeed or raise with unchanged live state; this change does
not introduce size/depth quotas or truncate unbounded input iterables.

### Compatibility and qualification matrix

Keep the exact runtime dependency `pydantic==2.13.4`; do not independently pin
pydantic-core or claim support for neighboring Pydantic versions. Fail early with
the compatibility diagnostic if the installed Pydantic version is unsupported.
Inspect the required adapter structures before using them; an incompatible shape
must not fall back to unchecked validation. Record the resolved pydantic-core.
Keep FastAPI/httpx/Pyright development pins; these are not runtime dependencies.

Required blocking runtime lanes, all running the production suite:

| Runner | CPython minors |
| --- | --- |
| `ubuntu-latest` | 3.11, 3.12, 3.13, 3.14 |
| `macos-latest` | 3.11, 3.14 |
| `windows-latest` | 3.11, 3.14 |

This qualifies the named runner environments, not every operating-system version
or Python implementation. Run production wheel and sdist-rebuilt-wheel consumers
on Ubuntu 3.11 and 3.14. Run strict source/consumer typing with pinned Pyright on
Ubuntu 3.11. Keep docs/lint/format gates; artifacts and negative typing become
mandatory for ordinary CI as well as releases. `ci.yml` continues to call
`check.yml` on every push/PR; release still calls the same complete checks before
building/publishing. Preserve tag/version matching and Trusted Publishing permissions.

## Invariants

Existing [I1–I8](mutation-semantics.md#invariants) remain required: validated state,
one authoritative store, declared field presence, complete rollback, atomic bulk
updates, guarded mutable escape paths, ancestor validity and observational
serialization. This change adds these bounded verification obligations:

- Every supported declared mutable API matches its guarded runtime ABC.
- No partially built candidate escapes via a public copy or operation result.
- Same-root guards and internal ContextVars recover after every failure boundary.
- Schema caches are class-local, reused without repeated compilation, and reset
  when a supported complete-schema rebuild replaces their source schema.
- Current-node bookkeeping is proportional to reachable owned nodes, not historical
  mutations; retained handles keep their root alive and unreachable graphs collect.
- A passing typing gate analyzed the intended files and checked expected errors;
  a passing artifact gate imported the installed production distribution.

## Acceptance criteria and verification matrix

Each AC is a release boundary for this change. Existing test counts are a baseline,
not a target number; migrate intentional alpha-breaking cases without dropping
their behavioral assertions. No required AC may be hidden behind a skip/xfail.

| ID | Observable acceptance criterion | Preferred proof |
| --- | --- | --- |
| AC-001 | ABC mutable fields, nested ABCs, safe scalar/nullable/Annotated/Literal fields, tuple/frozenset aggregates, finite recursive models and specialized generics construct with conforming runtime values from supported ordinary inputs. | Contract/unit: annotation matrix, runtime ABC assertions, static attribute assertions and recursive/generic fixtures. |
| AC-002 | Concrete mutable field annotations, including aliases and nested/union/generic occurrences, and unspecialized generic instance construction fail with `pydandict_unsupported_annotation:` before an instance escapes; documented ABC and explicit-specialization migrations accept the supported payload. | Contract/static: rejection matrix, deferred-forward completion, implicit-generic construction rejection and runnable migration fixtures. |
| AC-003 | Cycles, arbitrary/custom/ordinary-BaseModel values, unsafe hash keys/members and custom timezone payloads fail at input/output ownership boundaries; mutator/copy failures preserve the original root. | Unit/property: broad Any/typed-extra inputs, validator-created unsafe output, tuple/frozenset/key/member cases and recovery. |
| AC-004 | Disabled validation/default/instance-revalidation settings, unsupported hooks, conflicting stored-extra overrides and protected/alias-colliding names fail with the specified category/code; supported extra policies retain input/mutation behavior. | Contract/unit: configuration, inherited namespace, aliases and typed-extra matrices with BaseModel controls. |
| AC-005 | Existing nominal identities, canonical key ordering, attribute/key equivalence, declared-field presence, model equality and mutable/frozen-safe hashing match the contract. | Runtime/static compatibility: production API fixtures and matched BaseModel controls. |
| AC-006 | Coupled update commits its whole valid candidate; malformed/late-failing input commits nothing; duplicates/kwargs/self-update behave as specified; empty model updates/resets and existing-key setdefault invoke no validators. | Unit/contract: bounds model, failing generator, duplicate precedence, self operands and invocation counters. |
| AC-007 | Invalid root/descendant edits, ancestor constraints and frozen boundaries leave values, order, fields-set, caches, handles and ownership unchanged; a subsequent valid write succeeds. | Unit/property: expanded parent/freeze matrix and independent plain-data stateful oracle. |
| AC-008 | Non-idempotent untouched scalar drift and unexpected retained topology changes fail before commit with the corresponding diagnostic; canonical-safe normalizers retain valid behavior on changed inputs. | Differential/contract: before/after/plain/wrap and annotated validator fixtures with explicit unsupported controls. |
| AC-009 | Public Python/JSON/strings strictness, aliases and supplied construction context follow the pinned control behavior; transactions/copies validate in Python mode with no retained context. | Compatibility/integration: mode/alias/context matrix, normalization counters and context-required rejection/recovery. |
| AC-010 | External mutation cannot alter adopted state; repeated mutable inputs detach; saved handles follow retained nodes through reorder/unrelated changes and reject reads/writes after replacement/removal/union-branch change. | Unit/property: nested model/container identity matrix and generated reorder/adoption operations. |
| AC-011 | Supported augmented assignments through attributes, keys and nested slots perform one root validation/commit; manual exact-handle assignments are policy-checked no-ops; identical frozen writes fail; bulk same-handle updates remain replacements. | Contract: commit/validator counters, nested model/container slots, frozen identity and self-referential operands. |
| AC-012 | Model key iterators follow their own structural version; container iterators invalidate after any committed root edit; failures/no-ops preserve them; creation-before-first-next and permanent exhaustion behave as specified. | Unit/contract: model, list/dict/set, reverse and live-view iterator matrix. |
| AC-013 | Successful model/container pop/popitem returns a usable detached graph with independent nested model roots, stales old handles, and respects parent validation; result-preparation failure leaves all old state live. | Unit/property: nested removals, return mutation and injected preparation failures. |
| AC-014 | All supported model copies validate/detach mutable state; guard deepcopy produces usable independent nested models; shallow conversion retains guarded descendants without exposing raw payloads; trusted bypass paths remain rejected. | Contract/compatibility: copy/deepcopy/adoption matrix, stale originals, frozen-source updates, deprecated warnings and pickle/construct rejection. |
| AC-015 | Successful nested edits mark containing ancestors explicit; reset/default factories and cached computed values follow the specified lifecycle; metadata snapshots cannot alter metadata, and failure preserves cache identity. | Differential/unit: exclude_unset, data-dependent/failing factories, duplicate reset, metadata edits and saved cached values. |
| AC-016 | Library diagnostics expose the specified prefixes/categories or validation-policy codes without raw state; missing/frozen/protected/error precedence follows the mutation contract; validator programming exceptions propagate unchanged. | Contract/unit: exact leading codes/error types, Pydantic error locations, redaction and recovery. |
| AC-017 | All version-sensitive state/schema/cache operations use the compatibility boundary; canonical aliases, generic/recursive refs and public serializers survive supported schema rebuilds; unsupported version/shape raises the compatibility diagnostic rather than using unchecked fallback. | Adapter compatibility/static review: focused schema/slot fixtures, class-local cache/compile counters, rebuild before use and simulated incompatible version/shape. |
| AC-018 | Pydantic dumps/JSON/schema preserve supported alias/exclusion/default/context/computed/custom-serializer behavior and reveal no ownership metadata; mapping reads bypass serializers; unsupported direct guard encoding fails visibly. | Differential/contract: matched BaseModel payloads, schema modes, serializer invocation and TypeAdapter/JSON guard cases. |
| AC-019 | TypeAdapter, nested ordinary BaseModel envelopes and real FastAPI requests return guarded production models; invalid requests produce expected 422 responses and response/OpenAPI payloads preserve supported constraints/aliases. | Integration: TestClient request/response/OpenAPI controls, response annotation/filtering and nested collections. |
| AC-020 | Same-root mutation/copy reentry from generators, sort keys and validators is rejected before live mutation; reads see committed state; any BaseException before/during commit restores state and releases guards/ContextVars. | Unit/property: callback probes, unrelated-root construction afterward, MemoryError/KeyboardInterrupt injection and recovery. |
| AC-021 | Failure immediately before and after every prepared slot swap restores the original state/handles; old storage/cache disposal occurs after swaps and callbacks never observe a half-committed root. | Fault/contract: enumerate prepared swaps on a nested fixture, inject each boundary, trace retained-cache finalizers and perform a later valid write. |
| AC-022 | A retained live handle keeps its root alive; releasing all external references collects the graph; 500 replacements collect discarded handles and leave current bookkeeping bounded by current reachable owned nodes. | Lifecycle/property: weakrefs, gc and node-count assertions for success/failure/replacement sequences. |
| AC-023 | Strict Pyright analyzes every production source file plus the positive fixture and new qualification helpers with zero unexpected errors; installed public completeness is 100%; no broad suppression hides private-source failures. | Static gate: include directory coverage, filesAnalyzed/path checks, strict source run and installed verifytypes; review unavoidable boundary Any and scoped iterator override. |
| AC-024 | The negative typing gate analyzes its fixture and verifies exactly the expected rule/location diagnostics, including all four existing errors; zero analyzed files, absent diagnostics or unexpected diagnostics fail the gate. | Static/contract: independent fixture config outside normal exclusion, JSON rule/line comparison and verifier failure controls. |
| AC-025 | Every push/PR and release call blocks on the declared eight runtime lanes, docs/lint/format, actual typing and production artifact consumers; a failed required lane prevents downstream publication. | CI/integration: successful candidate workflow, reusable dependencies/needs review and scripts that return nonzero on missing proof. |
| AC-026 | Direct production wheel and sdist-rebuilt wheel install into clean external environments; isolated library/HTTP/typing consumers import site-packages `pydandict`, pass, and record exact resolved dependencies/artifact hashes without source/prototype path fallback. | Packaging/integration: Ubuntu 3.11/3.14 consumers with PYTHONPATH removed, explicit import-path/package-root assertions, Twine and py.typed/archive checks. |
| AC-027 | A reproducible production benchmark report measures the defined large/deep workloads for baseline and candidate on the same environment, with valid result assertions, latency/allocation/validation counts and complete metadata; no unmeasured speed or budget claim is made. | Benchmark/property: workload correctness checks, three comparable runs and machine-readable report; timing is observational in this phase. |
| AC-028 | Target contracts, migration examples, supported matrix, diagnostics and decision statuses agree with demonstrated behavior; the evidence record maps every AC to an actual result and preserves historical prototype records. | Documentation/static/contract: tools/check_docs.py, runnable migration, AC trace table and final evidence review. |

## Implementation phases

### P02-1 — Establish contract fixtures and close typing coverage holes

Goal: make the two observed typing gaps visible and pin the behavioral boundary
before reorganizing code. No dependencies on later phases.

- Relevant files: `pyproject.toml`, production `tests/`, new
  `tools/check_typing.py`, `check.yml` typing entry point.
- Include all `src/pydandict` production modules, the positive fixture and new
  qualification helpers in strict analysis. Runtime tests intentionally containing
  invalid writes, prototype experiments and unrelated probe tools do not need to
  be converted wholesale to strict code.
- Type private handles generically and define operation/root protocols. Quarantine
  unavoidable Pydantic schema/storage `Any` in the adapter and matching public
  Pydantic signatures; internal control/data flow uses annotated types. Do not
  silence strictness with file-wide ignores, blanket diagnostic disabling or
  exporting `Any`. Keep the justified iterator override suppression local.
- Build a real negative checker: use a dedicated generated config whose include
  is the copied fixture and whose exclude is empty; parse JSON and compare the
  complete error multiset of rule and source line to annotated expectations.
  Require the expected nonzero Pyright exit, one analyzed negative fixture, no
  unexpected errors, and fail on empty output. This replaces the misleading direct
  invocation of an excluded file. Use the same verifier for installed consumers.
- Add focused fixtures/counters for annotation policy, exact-handle writes,
  iterators, guard deepcopy and every error prefix. Existing runtime tests stay
  behavioral regression controls; do not weaken assertions to make new fixtures pass.
- Proof: AC-023/024 and baseline portions of AC-005/006. A working intermediate
  commit must not report excluded negative fixtures as verified.

### P02-2 — Isolate and qualify the compatibility boundary

Goal: separate version-sensitive mechanics without changing supported transaction
behavior. Depends on P02-1's regression/typing controls.

- Relevant modules: `_compat.py`, `_core.py`, `_ownership.py`, `_transaction.py`.
- Move raw allocation/storage/schema/cache/serializer/swap operations behind the
  adapter. Preserve the outer recursive schema reference, canonical alias removal,
  explicit public alias flags and fields-set restoration; document each private
  dependency and its dedicated fixture.
- Validate supported version and required adapter shapes, isolate class-local
  caches, and invalidate them after a successful complete-schema rebuild. Normal
  writes must not recompile validators. Do not claim support for a simulated
  neighboring version merely because its failure path is tested.
- Keep full-root validation and the existing prepared-swap rollback strategy.
  Replace prototype-only fault plumbing with private monkeypatchable test seams
  if useful; do not create a supported production fault-injection API.
- Proof: AC-017/018, repeated cache/rebuild/generic/recursive/alias checks and
  migrated existing source-fault tests. No persistent-state migration is needed.

### P02-3 — Enforce the annotation, value and validator contracts

Goal: make owned runtime values match supported declared types and provide stable
safe failures. Depends on P02-2's complete-schema and raw-state adapter.

- Relevant files: `_core.py`, `_ownership.py`, `_compat.py`, positive/negative
  fixtures and production annotation/validator contract tests.
- Check complete resolved field annotations recursively, including unions,
  Annotated, tuple/frozenset, generic specialization and typed-extra value schemas.
  Reject concrete mutable and unsupported value declarations before safe instance
  construction; allow deferred forward completion under the pinned Pydantic hooks.
- Port existing production concrete-field tests to equivalent ABC declarations
  while preserving operation/serializer assertions. Add separate explicit concrete
  rejection/migration cases. Do not edit the historical prototype implementation.
- Audit exact leaves, timezones and hash-position values on both ingress and
  validated output. Retain cycle detection and independent alias adoption.
- Preserve whole-model Pydantic ordering, untouched-state drift/topology detection,
  canonical Python/context-none mutation and current hook restrictions. Add each
  supported validator-form fixture and unsupported counterexample; do not promise
  automatic inference of purity, determinism or external effects.
- Apply the specified error prefixes and policy codes without wrapping arbitrary
  callback exceptions. Update the affected typing/ownership/API and migration docs.
- Proof: AC-001–004, AC-008/009/016, plus existing construction/union/generic tests.

### P02-4 — Harden operation, handle and failure lifecycle

Goal: close the supported mutation/copy/iterator escape paths and prove recovery.
Depends on P02-3's field/value/validator contract.

- Relevant modules: `_transaction.py`, `_ownership.py`, `_containers.py`, `_core.py`;
  stateful, iterator, copy/removal, callback and slot-failure tests.
- Centralize exact-owned-handle no-op checks with liveness/freeze/policy checks
  for model and container slots, including nested models; keep bulk replacement
  semantics distinct. Validate augmented assignment once without bytecode tricks.
- Specify and implement conservative root-commit container generations, local
  ordered-key model generations and permanently exhausted iterators.
- Prepare deep-copy/removal results as detached usable graphs with installed
  nested roots. Preserve the documented guarded descendants in shallow results.
- Acquire guards before input callbacks; restore after every BaseException; retain
  old values/caches across swaps; perform old-state disposal after swaps while busy.
- Enumerate all swaps on a multi-node fixture and inject before/after each swap.
  Extend the independent oracle with nested child changes, removals, reset,
  handle retention, reorder, copies, stale reads and failure recovery. Include
  maximum configured collection boundaries and deep finite graphs; on exhaustion
  or RecursionError require unchanged state, not a new quota system.
- Verify weakref collection and bounded ownership accounting after 500 replacements.
- Proof: AC-005–007, AC-010–015 and AC-020–022. Document lifecycle choices in
  mutation/ownership docs without broadening arbitrary user-cache support.

### P02-5 — Qualify the production package and required CI matrix

Goal: replace prototype-only artifact evidence and incomplete runtime coverage with
blocking production checks. Depends on P02-1–4 passing local contracts.

- Relevant files: `tools/qualify_package.py`, production consumer fixtures,
  `tools/check_typing.py`, `check.yml`, compatibility/testing/release documentation.
- Use `sys.executable`, standard-library venv and platform-appropriate executable
  paths. Do not require uv or a POSIX-only `.venv/bin/python` in the helper.
- Build root wheel/sdist into a fresh temporary directory; inspect metadata and
  `py.typed`, run Twine, safely extract the generated sdist, and rebuild its wheel.
  Never qualify stale globbed artifacts from a previous run.
- Copy isolated consumers outside the checkout, clear source/prototype import
  paths, install production artifacts and only necessary consumer dependencies,
  and assert the imported package and verifytypes package root are in the clean
  environment. Bare library use must not require FastAPI. Run both library and
  HTTP consumers for each artifact, plus installed positive/negative/completeness
  checks. Retain Pydantic as the sole direct runtime dependency.
- Run the eight runtime lanes specified above with fail-fast disabled for useful
  failure evidence, mandatory Linux typing and Linux-bound artifact lanes.
  `check.yml` remains the single reusable checks entry point; preserve the
  release-only package preflight input and its downstream publish dependencies.
- Record exact Python, OS/runner, Pydantic/core, FastAPI/Starlette/httpx, Pyright
  and tool versions per environment. No unsupported dependency range is introduced.
- Proof: AC-019, AC-023–026 and CI-specific AC-025. A workflow success must mean
  all required proofs ran, not that an empty or conditional gate was skipped.

### P02-6 — Record measurements, evidence and contract finalization

Goal: provide the next phase a measured, traceable baseline. Depends on P02-5's
qualified production implementation; no performance optimization is required.

- Relevant files: `tools/benchmark_phase02.py`, new Phase 0.2 results/report under
  `docs/research/`, affected documentation, decisions and changelog.
- Compare unmodified baseline `07fec9b` and candidate source on the same machine,
  Python and resolved dependencies using ABC model fixtures that both accept.
  Do not compare a production candidate to prototype-import artifacts or reuse
  the prototype timing numbers as same-machine baseline data.
- Required shapes: flat mutable sequences of 10/100/1,000/10,000 safe elements;
  linear nested model/sequence chains of depth 1/5/20, each level holding two
  scalar leaves and at most one child in a sequence (no exponential branching); a
  mixed sequence/mapping/set root under a pure parent sum constraint. Report
  graph/node counts so shape differences are visible.
- Required operations: key reads, scalar write retaining nested state, a coupled
  ten-field batch, rejected parent-invalid edit, nested leaf edit, copy, Python/JSON
  serialization. Assert the expected state/result before interpreting timings.
  Use at least five warmups and 100 timed samples per mutation/copy/serialization
  workload, 10,000 reads, and three complete runs per revision. Report median/p95,
  traced peak allocation measured separately, and root-validation invocation counts.
- Record machine/runtime/dependencies, workload input shape, source commit and
  hashes, warmup/sample/run settings, commands and observed variability. Phase 0.2
  timing has no cross-machine pass/fail ceiling and makes no speed guarantee;
  numeric beta budgets and cloning optimizations remain later work.
- Store a final evidence record at `docs/research/phase-0.2-results.json` and a
  readable `phase-0.2-findings.md`. Include each AC's proof/result, exact commands,
  CI run URLs, actual test/diagnostic counts, source/artifact hashes and resolved
  environments. Identify measured source commit plus dirty-tree status/hashes;
  generating the evidence file does not make its later commit the measured source.
  Never fill in unexecuted matrix results or overwrite prototype results.
- Update touched target documentation, decision statuses and migration guidance
  to verified behavior. Keep README/PyPI release facts separate from implementation
  completion; this step does not publish or tag 0.2.0.
- Proof: AC-027/028 and final review of every AC's recorded result.

## Risks and relevant failure modes

| Risk | Required handling / boundary |
| --- | --- |
| Alpha users declare concrete mutable fields | Explicit rejection and migration docs; ordinary input/serialized shapes remain stable. Do not quietly retain unsound attribute types. |
| Deferred references and specialized generic schemas | Audit complete schemas, test rebuild/cache isolation, and reject before an instance escapes; no mutation of live-instance schemas. |
| Canonical validators depend on JSON input, context or effects | Document exclusion, exercise pure counterexamples and preserve state on observable rejection; no promise to infer arbitrary semantics. |
| Reconciliation loses a moved child or aliases another root | Identity/origin tests and independent oracle; never match nodes using arbitrary user equality/hash. |
| Finalizers, callback errors and BaseException | Stage callbacks before commit, retain old storage through swaps, test disposal ordering and clear busy/ContextVars on failure. External effects are not rolled back. |
| Unsupported private Pydantic structures | Exact pinned support, boundary assertions, stable fail-closed diagnostic and compatibility tests; no fallback to unsafe public state. |
| Empty/missing/nullable/defaulted values | Existing API matrix stays required: required-nullable is not defaulted, absent pop fallback is untouched, protected declared fields do not disappear. |
| Copies/removal return incomplete candidates | Install independent roots in detached results before exposure and inject result-preparation failures. |
| Large/deep graphs or huge/infinite iterables | Measure finite cases, preserve state on ordinary resource exceptions, require caller limits where needed; no silent truncation or invented quota API. |
| Typing/artifact gates accidentally verify the wrong surface | Assert intended analyzed files, exact diagnostic multiset and site-packages import roots; require nonzero failure on absent proof. |
| Broader CI reveals a substantive in-scope regression | Fix or narrow the documented unsupported envelope through an explicit plan revision; do not pass via skips or dependency claims without evidence. |
| Benchmark noise | Three same-environment runs and separate correctness checks; measurements are evidence, not noisy CI speed blockers. |

## Explicit non-scope

- New public collections, TypedDict/per-key inference, code generation or checker plugins.
- Support for arbitrary BaseModels, enums/custom scalars/timezones, concrete built-in
  runtime identities, new ownership adapters or arbitrary hooks.
- Wider Pydantic/FastAPI/httpx/Pyright version ranges, prerelease lanes or alternate
  Python implementations; independently pinning transitive runtime dependencies.
- Thread/async safety, resource quotas, persistence/pickle, database migrations,
  authentication/authorization, reflection hardening or hostile-code containment.
- Expression-level rollback for augmented assignment into immutable tuple indices
  or read-only/computed properties; use supported named child mutators instead.
- Incremental validation, speculative cloning optimizations, numeric beta budgets,
  competitor benchmarks or claims that the entire v1 roadmap is complete.
- External trials, additional participants or independent adoption research.
- Publishing/tagging 0.2.0, changing release versions, GitHub Release creation,
  broad workflow/action upgrades or changes to Trusted Publishing permissions.
- Unrelated security-policy/metadata cleanup, whole-repository type/test rewrites,
  historical prototype refactoring or reopening later W06–W13 deliverables.

An unrelated defect discovered during review is follow-up work unless it prevents
these ACs from being satisfied safely. Such a dependency must name the affected AC
and justify a bounded plan amendment, rather than silently expanding this change.

## Known follow-up candidates

- [Issue #1: update the published-alpha security policy and establish private reporting](https://github.com/eddiethedean/pydandict/issues/1).
  `SECURITY.md` still says no public release exists; the GitHub API returned private
  vulnerability reporting disabled during this inspection. No open issue existed
  when duplicates were checked, so this focused follow-up was created. It does
  not alter the transaction/ownership implementation boundary or require trials.
- Broader upstream/platform qualification, extra safe value types, optional key
  inference and performance budgets remain the already documented later roadmap
  work, not newly confirmed defects or hidden Phase 0.2 requirements.

The 341 internal strict errors, excluded negative fixture and production-artifact
CI gaps are known pre-existing problems **inside this boundary** and must be fixed
here. The local editable-install/import setup failure is not a follow-up defect.
No additional unrelated substantive code defect was confirmed by this inspection.

## Definition of done

This change is done when AC-001–028 have actual passing evidence on the supported
matrix; required alpha compatibility and documented intentional breaks are
preserved; the existing regression behavior and required docs/lint/format/typing/
artifact gates pass; touched documentation matches demonstrated behavior; and no
known substantive regression or release blocker attributable to this change remains.
Any independently confirmed out-of-scope pre-existing failure is separately named
with evidence, not silently charged to this implementation or used to waive an
in-scope AC. The repository need not be globally defect-free.

No architectural question is deferred to the implementer: this change keeps
full-root transactions, private ABC guards, strong root retention, policy-checked
identity writeback, conservative container iterator invalidation, context-free
canonical mutations and exact pinned upstream support. Internal organization may
adapt within those requirements. Implementation and release verification still
need to be performed; this planning commit contains no production-code changes.

Implementation completed and independently reviewed; see the
[passed review](reviews/phase-0.2-rereview-6.md) and [release preparation](release.md).
