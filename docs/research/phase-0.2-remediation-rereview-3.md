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

After-fix verification: the same test passes. The historical third-review
verification passed with its then-current protected test set; later review
contracts are recorded separately below.

Related regression tests: the third-review base suite was historical evidence;
the current reconciled suite is reported below.

Resolution: each deferred stored declaration is independently resolved and sent
through the existing concrete-mutable annotation policy. The unresolved ClassVar
fixture now raises `pydandict_unsupported_annotation:` before an instance can
escape, while ClassVar remains exempt as required.

## SOL-008 — Final contract evidence is not reconciled

Status: **FIXED**  
Related AC: AC-027, AC-028

Root cause: final evidence was partially refreshed: readable benchmark summary
statistics, quality-gate counts, the measured-versus-qualified source narrative
and moved artifact proof paths did not all agree with the recorded evidence.

Production/documentation changes: no production code changed. The designated
`docs/research/phase-0.2-results.json` preserves the actual three baseline and
three candidate benchmark runs, including the dirty measured working tree based
at `7bf8383`. The readable findings now derive all displayed statistics from
those runs. It distinguishes that measured source from clean `a360bcc`, whose
identical package hashes were qualified by completed CI and both artifact lanes.
Artifact AC proof paths now refer to the retained lane records. Historical
measurements remain preserved.

Before-fix verification: `test_sol008_final_benchmark_identifies_the_qualified_candidate_source`
failed on three package hash mismatches.

After-fix verification: the earlier source/hash test and the new readable
summary contract pass. The benchmark protocol reports three runs per revision,
50 operation cells per run, five warmups, 100 timed samples (10,000 reads), ten
allocation samples and complete machine/dependency metadata. The current full
suite passes with 151 tests.

The local virtualenv still lacks pip/twine, so qualification was verified from
the completed hash-equivalent qualified-source Ubuntu 3.11/3.14 CI artifact
jobs instead.

## Quality gates

| Gate | Result | Notes |
| --- | --- | --- |
| Protected Sol and re-review tests | PASS | 37 review contract cases, including the final SOL-008 summary check, pass. |
| Base test suite | PASS | 151 passed, 2 dependency deprecation warnings. |
| New blocker verification | PASS | SOL-008 source/hash, CI identity and readable summary contracts pass. |
| Strict Pyright positive/negative | PASS | Eight positive files, four exact negative errors. |
| Public type completeness | PASS | 100%. |
| Ruff check/format | PASS | 24 files checked/formatted. |
| Documentation checks | PASS | 36 Markdown files, 210 links, 8 examples. |
| Production benchmark | PASS | Fresh three-run baseline/candidate execution recorded in JSON. |
| Qualified-source artifact qualification | PASS | Ubuntu 3.11/3.14 jobs for the hash-equivalent package source recorded direct/rebuilt consumers, hashes, dependencies and exact negative typing checks. |
| Qualified-source remote CI | PASS | Run 34862206206 completed all required lanes for the hash-equivalent package source. |

Blockers received: 2  
Blockers fixed: 2
Blockers remaining: 0
Verification conflicts: 0  
Escalations: 0
New follow-up candidates: 0

**READY FOR SOL RE-REVIEW**
