# Phase 0.2 blocker remediation report

This report records the bounded Luna remediation of the six blockers in the
latest Sol re-review. Sol's review and protected verification artifacts remain
unchanged.

## SOL-001 — Completed annotation envelope is not enforced

Status: FIXED
Related AC: AC-002
Root cause: The annotation audit inspected only the immediate Pydantic field
annotation. Named aliases and incomplete nested models could therefore expose a
resolved concrete mutable schema through a complete parent.
Production changes: `src/pydandict/_core.py` now unwraps `TypeAliasType` values,
tracks recursive alias checks, and audits compiled core schemas embedded in
incomplete nested `DictModel` classes, including typed-extra schemas.
Before-fix verification: Three protected `test_sol001_*` cases failed with
`DID NOT RAISE`; the supported `MutableSequence` alias control was also retained.

After-fix verification: All three SOL-001 protected cases pass, including the
concrete alias rejection and both deferred nested field/extra rejections.
Related regression tests: Full `tests/` suite and phase-0.2 contract tests pass.
Additional tests: The protected alias control proves that ABC aliases remain
supported while concrete aliases are rejected.
Resolution: Resolved concrete mutable annotations cannot escape through aliases,
deferred nested schemas, or typed extras, while supported abstract aliases remain
usable.

## SOL-002 — Unsafe hash-position ingress remains incomplete

Status: FIXED
Related AC: AC-003, AC-016
Root cause: `OwnedDict.setdefault` and iterable `update` materialized or probed
keys before the shared hash-position policy ran.
Production changes: `src/pydandict/_containers.py` now routes setdefault keys and
all mapping-update sources through `hash_input` before insertion or membership
hashing, while preserving mapping and iterable source semantics.
Before-fix verification: The two protected model-key cases raised native
`TypeError: unhashable type` without the required diagnostic prefix.
After-fix verification: Both cases pass with
`pydandict_unsupported_value:` and preserve state, handles, iterators, and later
valid insertion.
Related regression tests: Existing hash-ingress, copy, cycle, and phase-0.2
contract tests pass.
Additional tests: The protected setdefault and pair-update cases cover distinct
pre-hash insertion boundaries.
Resolution: Unsupported keys are rejected consistently before native hashing.

## SOL-006 — Artifact/matrix qualification is not complete

Status: FIXED
Related AC: AC-025, AC-026
Root cause: The required candidate workflow and Ubuntu artifact lanes had no
current execution record.
Production changes: No production change was required for this verification
blocker; the workflow and qualification helper from the prior remediation remain
enabled.
Before-fix verification: Local qualification passed, but current candidate CI
proof was absent (`current_candidate_run` was null).
After-fix verification: Local qualification passes after remediation and the
candidate workflow passed all eight compatibility lanes and both Ubuntu 3.11/3.14
artifact lanes in [GitHub Actions run 34846176558](https://github.com/eddiethedean/pydandict/actions/runs/34846176558).
Related regression tests: Full local suite, strict typing, package qualification,
and public completeness pass.
Additional tests: None; this blocker requires the actual remote matrix.
Resolution: The current candidate has traceable successful matrix and artifact
qualification evidence.

## SOL-008 — Final contract evidence is not reconciled

Status: FIXED
Related AC: AC-028
Root cause: Final evidence claimed completion while the SOL-001/002/010/012
verification and candidate matrix were still unresolved.
Production changes: No production change was required; this report records the
actual post-remediation test and gate outcomes without rewriting Sol's historical
review.
Before-fix verification: The final evidence audit found incomplete AC
reconciliation and no current candidate matrix result.
After-fix verification: All six protected blocker contracts pass, the full suite
reports 141 passed, and candidate CI run 34846176558 provides current matrix and
artifact results for commit `1cb73e031144948bb6907e1e944c8914deb40299`.
Related regression tests: Documentation, typing, package, and full-suite gates
pass locally.
Additional tests: None.
Resolution: Current local and remote outcomes are recorded without changing Sol's
historical review artifacts; the evidence now distinguishes the released 0.1.0
from this Phase 0.2 candidate.

## SOL-010 — Input materialization escapes the same-root guard

Status: FIXED
Related AC: AC-006, AC-007, AC-012, AC-020
Root cause: List-slice and mapping-update inputs were consumed before entering the
root transaction, allowing callbacks to mutate live state before late failure.
Production changes: `src/pydandict/_containers.py` now consumes slice and mapping
inputs inside `_change`; mapping sources are materialized and validated while the
root busy guard is held.
Before-fix verification: Both protected cases committed `marker = 9`, propagated
the late `ValueError`, and invalidated a saved iterator.
After-fix verification: Both cases pass with the reentrant-transaction diagnostic,
unchanged state and handles, preserved iterators, and successful recovery.
Related regression tests: Transaction remediation, callback, iterator, and full
phase-0.2 contract tests pass.
Additional tests: The protected slice and mapping-update cases establish the same
guard invariant across both input forms.
Resolution: Input callbacks are now bounded by the same root transaction and cannot
commit partial state before validation failure.

## SOL-012 — Existing-model public validation drops supplied context

Status: FIXED
Related AC: AC-009
Root cause: Existing `DictModel` inputs were sent through the context-free
canonical validator even when the public caller supplied validation context.
Production changes: `src/pydandict/_compat.py` now uses an info-aware schema wrapper;
`src/pydandict/_core.py` validates existing public models with the supplied context
and installs the already-validated result without a second canonical pass.
Before-fix verification: The protected differential case observed supplied context
for matched `BaseModel` but `None` for `DictModel`; the same mismatch reproduced on
the approved baseline.
After-fix verification: The protected case passes: raw and existing-model public
validation receive the supplied context, while subsequent mutation and copy remain
context-free.
Related regression tests: Full suite, context/serializer controls, and public type
completeness pass.
Additional tests: The protected matched-control test covers both public input
forms and verifies no context retention in later transactions.
Resolution: Public context behavior now matches the pinned Pydantic control without
retaining request context for canonical mutation or copy validation.

## Quality gates

| Gate | Result | Notes |
| --- | --- | --- |
| Protected blocker tests | PASS | 8 passed. |
| Related contract tests | PASS | 19 passed. |
| Full test suite | PASS | 141 passed in 101.28s, including the protected benchmark. |
| Strict typing | PASS | Positive and negative fixtures passed with exact diagnostics. |
| Ruff check and format | PASS | All CI-scoped files pass. |
| Documentation checks | PASS | 29 Markdown files, 195 links, 8 examples. |
| Public completeness | PASS | Pyright verifytypes 100%. |
| Artifact qualification | PASS | Local clean direct/rebuilt artifacts in four environments. |
| Current remote matrix | PASS | [Run 34846176558](https://github.com/eddiethedean/pydandict/actions/runs/34846176558): all eight compatibility lanes, both Ubuntu artifact lanes, docs and quality gates passed. |

Blockers received: 6
Blockers fixed: 6
Blockers remaining: 0
Verification conflicts: 0
Escalations: 0
New follow-up candidates: 0

**READY FOR SOL RE-REVIEW**
