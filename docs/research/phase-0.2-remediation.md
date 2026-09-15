# Phase 0.2 blocker remediation report

This report records the Luna remediation pass for the nine blockers in the Sol
review. Sol's review artifact and verification tests remain unchanged.

## SOL-001 — Completed annotation envelope is not enforced

Status: FIXED  
Related AC: AC-002  
Root cause: Annotation checking ran only during initial subclass setup and skipped
typed extras, completed forward references and nested unbound generic models.  
Production changes: `src/pydandict/_core.py` now audits typed extra value
annotations through the adapter's completed Pydantic metadata (including inherited
and generic substitutions), audits completed fields from `model_rebuild`, and audits nested
annotations at public schema entry.  
Before-fix verification: Three `test_sol001_*` cases failed with no TypeError.  
After-fix verification: All three cases pass with the required prefix.  
Related regression tests: `tests/test_phase02_contract.py`, full `tests/` suite.  
Additional tests: `tests/test_extra_annotation_completion.py` adds four cases for
future annotations, deferred extra completion, generic substitution and inherited
unspecialized model extras. The existing Sol verification is preserved.  
Resolution: Concrete mutable annotations and unspecialized generics cannot escape
supported construction, including deferred and nested paths.

## SOL-002 — Unsafe models are accepted in hash positions

Status: FIXED  
Related AC: AC-003, AC-014, AC-016  
Root cause: Cloning did not distinguish hash positions from ordinary descendants.  
Production changes: `src/pydandict/_core.py` propagates a hash-position flag through
dict keys, sets, frozensets and tuples and rejects DictModels/owned guards.
Single-key/member ingress checks hash safety before native hashing.  
Before-fix verification: Three key/member cases accepted invalid graphs.  
After-fix verification: All three cases pass, preserving state and recovery.  
Related regression tests: Existing cycle, unsafe-value, copy and serialization tests.  
Additional tests: `tests/test_hash_ingress.py` adds three unhashable model cases
for direct mapping assignment, set.add and generator set.update, proving rejection
before native hashing and subsequent recovery.  
Resolution: Unsupported models and guards fail before ownership commit with the
documented unsupported-value diagnostic.

## SOL-003 — Identity assignment is incomplete and bypasses ancestor policy

Status: FIXED  
Related AC: AC-007, AC-011  
Root cause: Container shortcuts recognized only Owned guards, and model shortcuts
checked only the local write policy.  
Production changes: `src/pydandict/_containers.py` recognizes both handle families;
`src/pydandict/_core.py` routes model identity through the root ancestor check.  
Before-fix verification: Two identity cases replaced/staled children and the
frozen ancestor case succeeded.  
After-fix verification: All three cases pass with preserved identity, iterators and
frozen-instance errors.  
Related regression tests: Inventory, augmented-assignment and frozen ancestor tests.  
Additional tests: No new implementation-side cases; the existing Sol verification is preserved.  
Resolution: Exact single-slot handles are policy-checked no-ops; bulk updates remain
ordinary replacements.

## SOL-004 — Compatibility isolation and rebuild lifecycle are unfinished

Status: FIXED  
Related AC: AC-017, AC-023, AC-016  
Root cause: Version-sensitive allocation, schema rewrites, slot operations and
compiled caches escaped the adapter; broad private Any annotations hid ownership
and transaction contracts.  
Production changes: `src/pydandict/_compat.py` owns checked raw storage,
allocation, swaps/restoration, schema wrappers/rewrites/serializer delegation and
class-local canonical/alias caches. Successful rebuild invalidates both caches;
cache schema identity also prevents stale reuse. `_containers.py` now has generic
payload/element/key/value guards and a typed callback coordinator. `_core.py`
uses object values, typed paths/callbacks/return types and explicit narrowing.  
Before-fix verification: The original Sol run failed all three `test_sol004_*`
controls. At the start of this continuation their runtime fixes passed, but static
inspection still found broad private Any and schema/cache ownership in core.  
After-fix verification: All three protected controls pass. Strict Pyright analyzes
eight files with zero errors; private guard/transaction annotations contain no Any.
Storage corruption, malformed wrappers, class-local canonical rebuilds and public
JSON Schema metadata are also verified.  
Related regression tests: Full runtime suite, protected alias/schema/AST controls,
strict source and installed type-completeness gates.  
Additional tests: `tests/test_compat_remediation.py` adds ten cases for canonical
cache isolation/rebuild, corrupt slots, malformed consumed schemas and preserving
JSON Schema examples, explicit caller-frame rebuilds and automatic deferred
completion through Python/JSON/strings validation. `tests/typing_positive.py` proves generic reads/results,
sort callbacks and coordinator return inference.  
The 500-replacement case in `tests/test_transaction_remediation.py` also proves
that typed coordinators release discarded guards and bound current bookkeeping.  
Resolution: The complete adapter and private typing requirements are implemented.
Schema checks distinguish validation nodes from user metadata and serialization
schemas, preserving supported Field/schema/serializer behavior.

## SOL-005 — Typing verifier accepts incomplete or unexpected proof

Status: FIXED  
Related AC: AC-023, AC-024  
Root cause: Positive checks used a two-file minimum and negative diagnostics were
deduplicated into a set while malformed errors were skipped.  
Production changes: `tools/check_typing.py` verifies complete source/helper count,
exact error exit/count and a diagnostic multiset with locations/rules. It also
checks intended strict include/exclude configuration and negative fixture paths.  
Before-fix verification: Three fabricated incomplete/duplicate/unruled reports
passed.  
After-fix verification: All three controls fail as required; real typing gate passes.  
Related regression tests: Installed verifytypes and strict project run.  
Additional tests: No new implementation-side cases; the existing Sol verification is preserved.  
Resolution: CI can no longer pass on incomplete or unexpected Pyright evidence.

## SOL-006 — Artifact qualification exercises only one wheel

Status: FIXED  
Related AC: AC-025, AC-026  
Root cause: Qualification installed only the direct wheel and did not execute the
typing import-root assertion or installed negative/completeness checks.  
Production changes: `tools/qualify_package.py` now qualifies both wheels in separate
bare and HTTP environments, executes runtime typing consumers, runs verifytypes and
negative typing, checks py.typed, and records pip freeze plus hashes.  
Before-fix verification: Mock orchestration observed one installed wheel.  
After-fix verification: Protected orchestration test passes; real qualification
passed for direct and rebuilt artifacts with isolated consumers and dependency records
on macOS/Python 3.11. Configured Ubuntu 3.11/3.14 lanes have not run for this dirty tree.  
Related regression tests: Full package suite, Twine/build and FastAPI integration.  
Additional tests: No new implementation-side cases; the existing Sol verification is preserved.  
Resolution: Both production artifact forms are now installed and exercised without
source-path fallback.

## SOL-007 — Benchmark is not the approved production comparison

Status: FIXED  
Related AC: AC-027  
Root cause: The prior tool timed one abbreviated workload against a plain dict;
baseline labels and workload dimensions did not constitute production measurements.  
Production changes: `tools/benchmark.py` extracts the unmodified production source
at `07fec9b7eafef5b00befe9fa24ccd012ce0232a1` and snapshots candidate source.
Separate processes run the same ABC fixtures and resolved interpreter/dependencies,
asserting import roots and source hashes. CI checkout fetches the history required
for this source comparison.  
Before-fix verification: The original protected baseline test failed. Inspection at
the start of this continuation confirmed that the subsequently added labels still
left a plain-dict baseline and unmeasured width/depth/operation declarations.  
After-fix verification: The protected baseline contract passes. The full report
contains 50 applicable shape/operation cells in each of three runs per revision:
flat widths 10/100/1000/10000, linear depths 1/5/20 and the mixed constrained root.
Every warmup/sample checks state/results. Timing uses five warmups, 100 mutation,
copy and dump samples and 10,000 reads per shape/run; ten separate allocation
samples exclude tracemalloc and verification from latency timing.  
Related regression tests: Protected `test_sol007_*`, full suite, strict helper
checking and benchmark evidence validation.  
Additional tests: `tests/test_benchmark_contract.py` checks all required shapes,
graph counts, applicable operation coverage, parent rejection and coupled-batch
correctness/counts.  
Resolution: Reports include median/p95, traced peaks, actual per-phase root
validation counts, source/harness hashes, exact commands, environment/dependencies
and three-run variability. Ten-field/rejected-parent operations run on the mixed
root; shapes without those constraints explicitly mark them inapplicable. A
distinct root schema in the linear fixture measures root invocations separately
from recursive child schemas. No speed guarantee or numerical ceiling is claimed.

## SOL-008 — Contract documentation and AC evidence are unfinished

Status: FIXED  
Related AC: AC-028  
Root cause: Required evidence files were absent and affected documents/decisions
still described Phase 0.2 as a future proposal.  
Production changes: Added `docs/research/phase-0.2-results.json` and its readable
findings companion; finalized affected ownership, mutation, compatibility, testing
and decision language; separated the published 0.1.0 fact from unreleased candidate evidence.  
Before-fix verification: Evidence presence test failed.  
After-fix verification: Evidence presence, JSON parsing and documentation checks pass.  
Related regression tests: `tools/check_docs.py`.  
Additional tests: No new implementation-side cases; the existing Sol verification is preserved.  
Resolution: Every AC has a trace entry and historical prototype records are retained.

## SOL-009 — Old cache storage survives beyond the guarded commit

Status: FIXED  
Related AC: AC-021  
Root cause: The recursive preparation closure retained obsolete storage through a
self-cycle until cyclic garbage collection.  
Production changes: `src/pydandict/_core.py` breaks the preparation closure cycle
on success and failure before returning or raising.  
Before-fix verification: Cache finalizer observed `(2, 3, False)`.  
After-fix verification: Protected disposal test observes `(2, 3, True)`; the new
enumerating test passes 82 before/after injections over all 41 prepared swaps.  
Related regression tests: Fault-injection, reentry and lifecycle tests.  
Additional tests: `test_every_prepared_swap_boundary_recovers` enumerates all
prepared slot positions and verifies state, four handles, busy/ContextVar cleanup
and a subsequent valid write after KeyboardInterrupt on both sides of every swap.  
Resolution: Obsolete storage can finalize only within the guarded commit lifecycle.

## Follow-up report

### Existing Sol FOLLOW-UPs

[Issue #1](https://github.com/eddiethedean/pydandict/issues/1), security reporting
policy, remains outside this remediation and is not claimed fixed.

### New follow-up candidates

A self-recursive root class with an after validator can invoke that validator
twice during a write/copy. The same reproducer produces two calls on unmodified
baseline `07fec9b` and the candidate, so this is not caused by this remediation.
Location: the recursive schema/validation interaction in `_core.py`, and the
`Chain` fixture in `tools/benchmark.py`. Minimal reproducer:

```python
from tools import benchmark as b
model = b.Chain.model_validate(b._chain_input(5))
before = b._root_calls
model.left = 1
delta = b._root_calls - before
print(delta)
```

Current 0.3.0 output:

```text
1
```

The historical remediation run recorded two calls on both the unmodified baseline
and its candidate. The current 0.3.0 source returns one call for the same probe;
the snippet is retained as a historical control and now reports the observed
current value instead of asserting the older result.

## Quality gate report

| Gate | Executed | Result | Notes |
| --- | --- | --- | --- |
| Sol blocker tests | Yes | PASS | All 19 protected cases pass; review artifacts remain unchanged. |
| Full pytest suite | Yes | PASS | 133 tests in 95.08 seconds, including all blockers and 21 implementation-side cases. |
| Strict typing | Yes | PASS | Eight positive files, zero errors; four exact negative rule/line diagnostics. |
| Public completeness | Yes | PASS | Installed direct/rebuilt distributions and local verifytypes: 100%. |
| Ruff check/format | Yes | PASS | All CI paths; 19 Python files formatted. No broad ignores/exclusions added to neutralize failures. |
| Exploratory repository-wide Ruff | Yes | FAIL — PRE-EXISTING/UNRELATED | 16 findings in unchanged historical prototypes, check_docs.py and probe_upstream.py, outside the required CI lint paths. |
| Documentation check | Yes | PASS | Counts and exact command are in the evidence JSON. |
| Build/Twine/artifact qualification | Yes | PASS | Both wheels and sdist, four clean consumer environments. |
| Benchmark | Yes | PASS | 50 applicable cells, three complete runs for each real production revision. |
| Diff whitespace | Yes | PASS | `git diff --check`. |
| Other Python/OS CI lanes | No | NOT RUN — ENVIRONMENTAL/UNAVAILABLE | This local machine runs macOS/Python 3.11; previous remote CI URL is historical, not proof of this dirty tree. |

Exact commands, measured source identities, artifact hashes, dependencies and
unexecuted remote lanes are recorded in
[phase-0.2-results.json](phase-0.2-results.json). The full benchmark is preserved
in that evidence record. No follow-up or observation was opportunistically fixed.
No verification conflicts or architectural escalations remain in the blocker set.
The exploratory lint failures are established as unrelated by an empty diff for
all affected files. Historical controls and unrelated helper formatting were left
unchanged. There are no known unresolved implementation issues in the blocker set;
remote matrix verification remains unexecuted.

## Remediation summary

Blockers received: 9  
Blockers fixed: 9  
Blockers remaining: 0  
Verification conflicts: 0  
Escalations: 0  
New follow-up candidates: 1

READY FOR SOL RE-REVIEW
