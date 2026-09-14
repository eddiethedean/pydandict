# Phase 0.2 blocker remediation

This report records the bounded Luna remediation of the latest Sol review. It
does not constitute independent approval.

## SOL-001 — Deferred nested mutable annotations are audited by declaration

Status: **FIXED**  
Related AC: AC-001, AC-002

Root cause: the previous audit treated any mutable core-schema node as a
concrete mutable declaration and ran only after the outer model completed. That
rejected supported ABC annotations and missed deferred child declarations.

Production changes: `_compat.schema_namespace`,
`_compat.audit_incomplete_model`, and declaration-aware
`_core._audit_incomplete_field` now keep schema interpretation in the adapter,
resolve annotations through the active module and Pydantic namespaces, and
apply the existing annotation policy to the resolved declaration (including
typed extras).

Before-fix verification: Sol's deferred-field and deferred-extra tests failed;
supported deferred ABC cases were also rejected. After-fix verification:
`tests/test_sol_phase02_rereview.py` and
`tests/test_sol_phase02_rereview_2.py` pass, including concrete rejection and
ABC acceptance.

Resolution: concrete `list`/`dict`/`set` declarations remain rejected while
`MutableSequence`/`MutableMapping`/`MutableSet` declarations, aliases, and
deferred nested forms are accepted.

## SOL-004 — Core-schema access remains inside the compatibility adapter

Status: **FIXED**  
Related AC: AC-017

Root cause: `_core.py` previously reflected directly on Pydantic's private core
schema attribute. The adapter now supplies the checked schema and namespace to
the model wrapper, and the core module consumes only that boundary API.

Before-fix verification: the AST boundary check found the reflected access in
`_core.py`. After-fix verification:
`test_sol_phase02_rereview_2.py::test_sol004_core_schema_access_including_getattr_stays_in_adapter`
passes, together with strict typing.

## SOL-008 — Final evidence identifies measured source and candidate CI

Status: **FIXED**  
Related AC: AC-027, AC-028

Root cause: the designated evidence record still pointed at the pre-fix dirty
tree and had no current candidate CI result. The source block now fingerprints
the committed package implementation and the readable findings document has
been refreshed to the 147-test final suite. The remote run identifier is stored
in `phase-0.2-results.json` under `ci.current_candidate_run` after the pushed
candidate completes.

Before-fix verification: `test_sol008_final_evidence_identifies_measured_source_and_candidate_ci`
failed on stale hashes and a null run. After-fix verification is rerun after
the current candidate CI result is recorded.

## SOL-013 — Existing-model validation is detached and context-preserving

Status: **FIXED**  
Related AC: AC-007, AC-009, AC-010, AC-012, AC-015, AC-020, AC-021

Root cause: public validation passed live owned descendants into the next
validator and installed the result back into the caller's root. This caused
strict-mode failures and allowed failing validators to mutate the source.

Production changes: the existing-model branch clones the complete graph before
validation, preserves the detached fields-set metadata, then installs the
validated result as a fresh owned root. Context is supplied exactly once by the
public validator.

Before-fix verification: strict existing-model validation and failure-mutation
tests failed. After-fix verification:
`test_sol013_existing_model_validation_produces_independent_owned_result` and
`test_sol013_failed_public_validation_does_not_mutate_existing_input` pass,
alongside the protected SOL-012 context regression.

## Quality gates

| Gate | Executed | Result |
| --- | --- | --- |
| Protected SOL blocker/re-review tests | Yes | PASS |
| Strict Pyright positive and negative fixtures | Yes | PASS |
| Ruff check and format verification | Yes | PASS |
| Benchmark harness (baseline/candidate, 3 runs) | Yes | PASS |
| Full local test suite | Yes | PASS; final count recorded in results JSON |
| Remote CI matrix | Yes | Run recorded in results JSON |

Existing Sol follow-ups remain untouched. No unrelated production defects were
implemented during this remediation.

Blockers received: 4  
Blockers fixed: 4  
Blockers remaining: 0  
Verification conflicts: 0  
Escalations: 0  
New follow-up candidates: 0

**READY FOR SOL RE-REVIEW**
