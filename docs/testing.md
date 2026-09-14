# Testing and acceptance strategy

This is the production acceptance plan. The Phase 0.1 package has a root
[runtime, inventory and stateful suite](../tests/test_prototype.py), installed typing
checks and the original isolated artifact consumers. Its [recorded results](research/prototype-findings.md)
are scoped feasibility evidence, not completion of the production T1–T12 matrix.
The older upstream probes remain controls, not implementation safety tests.

## Test groups and release criteria

| Group | Coverage | Required evidence |
| --- | --- | --- |
| T1 Packaging | Import, wheel/sdist, dependency bounds, license, `py.typed` | Clean environment installs the built artifact |
| T2 Identity and reads | BaseModel/ABCs, ordering, views, attribute/key equivalence | Runtime and type assertions; mapping-only consumers |
| T3 Single writes | Valid/coerced/strict-invalid, fields/extras, both syntax paths | State and metadata equal before/after every failure |
| T4 Bulk mutations | update, iterable inputs, duplicate keys, keywords, `|=` | Coupled-field success; no partial state on any failure |
| T5 Destructive/default | del/pop/popitem/clear/reset/setdefault | Required/default/nullable/frozen matrix and factory failure |
| T6 Pydantic lifecycle | Validators, aliases, fields-set, copies, hooks, metadata access | Differential controls and documented divergences |
| T7 Ownership | Descendant paths, escaped aliases, parent validators, freeze | Full ordinary mutation inventory and isolation proof |
| T8 Serialization/framework | Dumps, schema, adapters, HTTP, OpenAPI | BaseModel comparisons and real FastAPI TestClient requests |
| T9 Interoperability | Generic Mapping/MutableMapping, dict/unpack, views, pattern match | Consumers contain no PydanDict-specific code |
| T10 Typing | Strict Pyright, public completeness, expected errors | Installed-package positive/negative fixtures |
| T11 Robustness/performance | Large inputs, cycles, exceptions, timing/memory | Reproducible benchmark report and failure tests |
| T12 Release/docs | Scope, support claims, examples, links, changelog | All published claims map to passing evidence |

## High-value examples

**Rejected assignment rollback:** after a model validator rejects a new value,
assert values, fields-set, extras, and owned handles are unchanged. Stock Pydantic
assignment is a counterexample in the recorded baseline.

**Coordinated change:** a `low <= high` model accepts `update(low=5, high=8)` from
`(1, 3)` and rejects `(9, 8)` without partial application. Test both input orderings.

**Late input failure:** a generator yields valid updates and then raises. Also
test malformed pair length and a non-string key after several valid keys. No
earlier item is committed.

**Canonical keys and serialization:** an aliased, excluded field remains a
canonical mapping entry. Its serializer changes output only; mapping reads and
candidate validation use the raw Python value. Test an alias resembling a method.

**Defaults and metadata:** omitted defaults are visible in the mapping but absent
from `exclude_unset` output. Assignment marks a field explicit; reset removes that
mark. Resetting a data-dependent factory uses candidate values in field order.

**Nested parent failure:** appending a valid item violates a sum/budget root
validator. Both the container and parent remain unchanged, including through a
saved `items()` value and `dict(model)` shallow-copy reference.

**External alias isolation:** mutate the input list or original child after
construction; the model does not change. Replace an owned field, then attempt a
write through its previous handle; it fails clearly.

**Copy safety:** `model_copy(update={'age': 'invalid'})` fails, while a valid copy
has independent mutable ownership. Copying a frozen model may create a new valid
instance without altering the original; invalid updates still fail.

## Parameterized mutation matrix

Cross every mutator with declared required/defaulted/nullable fields, allowed
typed/untyped extras, forbidden/ignored extras, aliases, frozen fields/models,
valid/coercible/invalid values, and field/model validator failure where applicable.
Include missing keys and existing keys separately. Track coverage of I1–I8 from
the [mutation contract](mutation-semantics.md).

Use Pydantic controls only for behavior intended to match. Explicitly assert
PydanDict differences such as key iteration, protected defaulted fields, validated
copy, and transactional rollback. A control model passing validation does not by
itself prove ownership, alias isolation, or mapping correctness.

## Property-based and stateful tests

Use Hypothesis to generate operation sequences over small representative schemas.
Keep a simple independent transition oracle: successful operations apply a whole
patch and validate; failures leave the previous expected state. Avoid an oracle
that merely calls the same transaction helper under test.

After every step compare key order, access values, metadata, and successful
revalidation for schemas whose validators are explicitly idempotent. Track stable
owned references and attempts to mutate stale ones. Generate cycles, repeated
aliases, slices, container in-place operators, empty updates, and failing iterables.
Shrink failures and keep the minimal counterexample as a regression test.

## Validator and hook adversaries

Cover before/after/plain/wrap field validators; before/after/wrap model validators;
field ordering and `ValidationInfo.data`; aliases/paths; nested instance
revalidation; context-sensitive validators; `model_post_init`; validator-returned
mutable values; and user exceptions. Include a doubling normalizer on an unchanged
field to expose accidental repeated normalization.

Unsupported combinations must be named in documentation and rejected where they
can be detected reliably. Validators with external side effects cannot be rolled
back; test isolation of model state without pretending external rollback exists.

## CI plan

Use pytest for units/integration, Hypothesis for stateful cases, Ruff for
formatting/lint, and strict Pyright for types. The Phase 0.1 package pins the
recorded Pydantic/FastAPI/httpx/Pyright envelope in its development extras and
the [`ci.yml`](../.github/workflows/ci.yml) entrypoint runs the reusable checks on
every push and pull request.

Run fast correctness/type checks on every PR. Run the supported dependency matrix,
artifact-install checks, and full integration suite before release. Add a periodic
upstream prerelease lane only when actual CI is introduced. Use relevant checks
for documentation-only PRs rather than rebuilding an unrelated package matrix.

## Qualification thresholds

These are proposed execution requirements for W10–W12, not achieved coverage or
timing claims. Keep coverage of the declared contract separate from line coverage.

| Check | Beta and 1.0 qualification requirement |
| --- | --- |
| Contract inventory | Every supported mutator and construction/copy/escape path has a test ID, applicable I invariants, and success/rejection/recovery cases; justify non-applicable cells |
| Correctness | Zero unresolved reproducible violations of I1–I8 within the advertised envelope; required cases cannot be skipped or marked expected failures |
| Branch coverage | Target at least 95% in transaction, ownership and compatibility modules; inspect every uncovered branch and document unreachable/platform-specific exclusions; percentage alone cannot close an invariant gate |
| Stateful sequences | At least 100 generated sequences of 100 steps for each representative schema family in release qualification; record settings and replayable failures, keeping shrunk regressions permanently |
| Fault injection | Cover each pre-commit boundary and supported rollback path, followed by a successful write proving recovery; inspect handle/metadata/cache state as well as values |
| Typing | Zero unexpected strict Pyright diagnostics and 100% public completeness on the installed package; negative fixtures assert diagnostic kind/location |
| Consumers | Both isolated consumer projects and all three quality-bar journeys pass from built artifacts without source imports or internal API access |
| Performance/memory | Meet the recorded numeric budgets selected before beta; publish baseline and candidate measurements with environment and variance |

Representative state-machine families are coupled scalar/default/extra records,
nested list/dict/set trees, and nested DictModel trees with ancestor/frozen/union
constraints. Use smaller deterministic smoke profiles on PRs and the full profile
for candidates. A count of generated sequences measures exercised workload, not
a mathematical proof or a claim of exhaustive coverage.

Inject failure during input iteration, default creation, validation, candidate
adoption, detached-result preparation and handle reconciliation. Exercise validator,
comparison, hashing, sort-key and finalizer callbacks where supported. Verify an
attempted same-root reentrant mutation is rejected before live changes and cannot
leave the transaction busy. An implementation that can fail midway through commit
must test restoration of each affected storage slot.

Add targeted test-sensitivity checks: temporarily disable validation, metadata
restoration, ancestor-freeze enforcement or stale-handle checks in isolated test
runs and verify the corresponding tests fail. Do not maintain a whole-package
mutation-testing percentage as a substitute for these safety checks.

Memory qualification includes repeated successful and rejected writes, replacing
subtrees, making/dropping copies, and retaining/releasing handles. After warmup and
garbage collection, inspect retained owners/nodes and compare measured allocation
growth with the selected budget. Test the eventual orphan/retention policy explicitly;
a process RSS sample alone cannot establish an ownership leak.

## Execution lanes

| Lane | Planned checks | Gate |
| --- | --- | --- |
| Documentation change | Local links/fences/Python syntax; released examples if changed | Required |
| Implementation PR | Lint, strict types, relevant unit/integration cases, stateful smoke and branch coverage | Required |
| Scheduled dependency check | Supported boundary matrix, extended stateful cases, upstream prerelease warning lane | Supported versions required; prereleases advisory |
| Release candidate | Full T1–T12, extended stateful/fault cases, all supported Python versions, dependency boundaries, artifact consumers and benchmark budgets | Required for publication |

Test every advertised Python minor on at least one supported platform; run OS
smokes on Linux, macOS and Windows before claiming those platforms. Dependency
boundary combinations must be compatible upstream combinations, not an impossible
Cartesian product. Record omissions instead of claiming untested platforms,
interpreters or prerelease runtimes. See the [compatibility matrix](compatibility.md).

## Documentation checks now

`python3 tools/check_docs.py` verifies local Markdown links and fragments, Python
example syntax, and closed code fences. It does not execute planned PydanDict
examples or prove their behavior. `tools/probe_upstream.py` records upstream
facts on installed dependencies. `tools/probe_typing.py` is a deliberately minimal
inheritance fixture; see [evidence](research/upstream-behavior.md).
