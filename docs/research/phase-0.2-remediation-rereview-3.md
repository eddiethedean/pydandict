# Phase 0.2 blocker remediation — third Sol re-review

This implementation report covers only SOL-001 and SOL-008 from
[Sol’s third re-review](../reviews/phase-0.2-rereview-3.md). It does not approve
the change or resolve unrelated follow-ups.

## SOL-001 — Completed annotation envelope is not enforced

Status: **FIXED**  
Related AC: AC-002

Root cause: `_audit_incomplete_field` resolved all model annotations in one
`typing.get_type_hints` call. An unrelated unresolved `ClassVar` caused that
call to fail, allowing a deferred stored-field `ForwardRef` to remain unchecked.

Production changes: `src/pydandict/_core.py`, `_audit_incomplete_field` now reads
the target declaration and resolves it through a synthetic single annotation,
using the active Pydantic namespace. Other unresolved model annotations no
longer suppress the target field audit; supported ABC and typed-extra paths are
unchanged.

Before-fix verification: `test_sol001_unresolved_ignored_classvar_cannot_bypass_deferred_field_audit`
failed because construction returned an owned list without raising.

After-fix verification: the same test passes. All 33 protected Sol/re-review
tests pass, including prior concrete rejection and deferred ABC acceptance cases.

Related regression tests: full base suite, 147 passed; strict typing gate passes.

Resolution: each deferred stored declaration is independently resolved and sent
through the existing concrete-mutable annotation policy. The unresolved ClassVar
fixture now raises `pydandict_unsupported_annotation:` before an instance can
escape, while ClassVar remains exempt as required.

## SOL-008 — Final contract evidence is not reconciled

Status: **PARTIALLY FIXED**  
Related AC: AC-027, AC-028

Root cause: the final record’s benchmark and readable findings referred to an
older dirty source despite newer remediation source hashes and CI claims.

Production/documentation changes: `tools/benchmark.py` was run to completion
against the updated tree (three baseline and three candidate runs). The
designated `docs/research/phase-0.2-results.json` now embeds that run and its
candidate source hashes; the readable findings report uses the refreshed
measurements and accurately labels parent-source CI/artifacts. Historical
measurements remain preserved in the prior record.

Before-fix verification: `test_sol008_final_benchmark_identifies_the_qualified_candidate_source`
failed on three package hash mismatches.

After-fix verification: the same test passes. The benchmark protocol reports
three runs per revision, 50 operation cells per run, five warmups, 100 timed
samples (10,000 reads), ten allocation samples and complete machine/dependency
metadata. The base suite remains 147 passed.

Remaining limitation: this working-tree fix has no current remote artifact run.
The local virtualenv has neither pip nor twine, so current clean wheel/sdist
qualification cannot be executed locally. Existing Ubuntu 3.11/3.14 artifacts
and CI are retained with their parent-source identity; a pushed commit is needed
to produce current-source remote artifact evidence and a current all-lane CI URL.

## Quality gates

| Gate | Result | Notes |
| --- | --- | --- |
| Protected Sol and re-review tests | PASS | 33 existing protected cases pass. |
| Base test suite | PASS | 147 passed, 2 dependency deprecation warnings. |
| New blocker verification | PASS | SOL-001 and SOL-008 both pass after remediation. |
| Strict Pyright positive/negative | PASS | Eight positive files, four exact negative errors. |
| Public type completeness | PASS | 100%. |
| Ruff check/format | PASS | 22 files checked/formatted. |
| Documentation checks | PASS | 33 Markdown files, 203 links, 8 examples. |
| Production benchmark | PASS | Fresh three-run baseline/candidate execution recorded in JSON. |
| Current-source artifact qualification | NOT RUN — ENVIRONMENTAL/UNAVAILABLE | Virtualenv lacks pip/twine; parent-source remote artifacts remain identified as such. |
| Current-source remote CI | NOT RUN — ENVIRONMENTAL/UNAVAILABLE | Existing successful run predates this working-tree fix. |

Blockers received: 2  
Blockers fixed: 1  
Blockers remaining: 1  
Verification conflicts: 0  
Escalations: 1 (current-source CI/artifact evidence requires a pushed commit)  
New follow-up candidates: 0

**REMEDIATION BLOCKED**
