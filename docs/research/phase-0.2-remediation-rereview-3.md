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

Status: **FIXED**  
Related AC: AC-027, AC-028

Root cause: the final record’s benchmark and readable findings referred to an
older dirty source despite newer remediation source hashes and CI claims.

Production/documentation changes: `tools/benchmark.py` was run to completion
against the updated tree (three baseline and three candidate runs). The
designated `docs/research/phase-0.2-results.json` now embeds that run, current
source hashes, the completed CI run and both current artifact qualifications; the
readable findings report uses the same measurements and AC outcomes. Historical
measurements remain preserved in the prior record.

Before-fix verification: `test_sol008_final_benchmark_identifies_the_qualified_candidate_source`
failed on three package hash mismatches.

After-fix verification: the same test passes. The benchmark protocol reports
three runs per revision, 50 operation cells per run, five warmups, 100 timed
samples (10,000 reads), ten allocation samples and complete machine/dependency
metadata. The base suite remains 147 passed.

The local virtualenv still lacks pip/twine, so qualification was verified from
the completed current-source Ubuntu 3.11/3.14 CI artifact jobs instead.

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
| Current-source artifact qualification | PASS | Current Ubuntu 3.11/3.14 jobs recorded direct/rebuilt consumers, hashes, dependencies and exact negative typing checks. |
| Current-source remote CI | PASS | Run 34862206206 completed all required lanes. |

Blockers received: 2  
Blockers fixed: 2
Blockers remaining: 0
Verification conflicts: 0  
Escalations: 0
New follow-up candidates: 0

**READY FOR SOL RE-REVIEW**
