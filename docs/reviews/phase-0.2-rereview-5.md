# Sol — Phase 0.2 fifth production re-review

Reviewed candidate: `1a2dd042269a28ea73a8b3dfb5d469009973e1c9` on `main`.
Review date: September 14, 2026.

The [approved plan](../phase-0.2-plan.md), its AC/verification matrix, P02-6
deliverables and explicit non-scope remain authoritative. This re-review
prioritizes SOL-008 from the [fourth review](phase-0.2-rereview-4.md), the
[updated implementation report](../research/phase-0.2-remediation-rereview-3.md)
and the actual final evidence. The latest remediation changes evidence and
verification only; production, workflow and qualification helper files are
identical to a360bcc. Publishing, optimization and existing unrelated issues
remain excluded.

Only this report and one blocker verification test were added during review.
Production, implementation-owned evidence and all previous Sol artifacts remain
unchanged.

## Acceptance criteria

| AC | Status | Evidence / remaining requirement |
| --- | --- | --- |
| AC-001 | VERIFIED | Supported annotation/runtime, recursive/generic and deferred ABC contracts pass. |
| AC-002 | VERIFIED | SOL-001 remains fixed; deferred concrete field/extra, alias/generic and ignored-ClassVar rejection controls pass. |
| AC-003 | VERIFIED | Closed-value, cycles, unsafe hash positions, adoption and recovery controls pass. |
| AC-004 | VERIFIED | Configuration/hooks, namespace/aliases and typed-extra policy controls pass. |
| AC-005 | VERIFIED | Model/mapping identities, canonical key/attribute behavior, equality and hashing pass. |
| AC-006 | VERIFIED | Atomic coupled updates, malformed input/generators, duplicates and no-op counters pass. |
| AC-007 | VERIFIED | Ancestor/frozen rollback and failed public validation isolation/recovery pass. |
| AC-008 | VERIFIED | Scalar drift/topology diagnostics and canonical-safe normalization pass. |
| AC-009 | VERIFIED | Public modes/strictness/aliases/context and canonical context-free controls pass. |
| AC-010 | VERIFIED | Detached adoption, repeated inputs, retained/reordered/stale handles and public result isolation pass. |
| AC-011 | VERIFIED | Augmented assignment, exact-handle no-op, frozen identity and commit-count controls pass. |
| AC-012 | VERIFIED | Model/container iterator lifecycle, no-op/failure and source isolation controls pass. |
| AC-013 | VERIFIED | Detached removals, ancestor validity and preparation-failure rollback pass. |
| AC-014 | VERIFIED | Model/guard copies and deepcopy, guarded conversion and bypass rejection pass. |
| AC-015 | VERIFIED | Fields-set/default/reset/cache metadata lifecycle controls pass. |
| AC-016 | VERIFIED | Diagnostic categories/codes, precedence/redaction and programming-exception propagation pass. |
| AC-017 | VERIFIED | Adapter version/shape/cache/rebuild and direct/reflected access controls pass. |
| AC-018 | VERIFIED | Dumps/JSON/schema, aliases/exclusions/context/computed/custom serializers and guard encoding pass. |
| AC-019 | VERIFIED | TypeAdapter/BaseModel/FastAPI request, 422 and OpenAPI controls pass; qualifying installed artifacts use identical production source. |
| AC-020 | VERIFIED | Same-root input callbacks/reentry, BaseException recovery and public validation detachment pass. |
| AC-021 | VERIFIED | Prepared-swap faults, rollback and guarded complete-state disposal pass. |
| AC-022 | VERIFIED | Retained-root lifetime, graph collection and 500-replacement bookkeeping pass. |
| AC-023 | VERIFIED | Eight-file strict positive proof, public completeness 100% and installed qualification pass. |
| AC-024 | VERIFIED | Exact four-error independent negative fixture and verifier failure controls pass. |
| AC-025 | PARTIALLY SATISFIED | Same production/workflow source passed all lanes at a360bcc; latest evidence/test commit run 34866518540 remains queued/in progress with no reported failures. |
| AC-026 | VERIFIED | Current final record includes both actual Ubuntu artifact lanes from a360bcc, which has identical production/helper source. |
| AC-027 | PARTIALLY SATISFIED | Complete JSON measurements are valid; readable baseline p95/allocation summaries still disagree with the recorded runs (SOL-008). |
| AC-028 | NOT SATISFIED | SOL-008: final counts/outcomes, measured-source narrative and some AC artifact proof paths remain unreconciled. |

Latest CI scheduling alone is not assigned a new blocker. The existing SOL-008
contract defect independently requires NEEDS FIXES.

## Previous blockers

| Finding | Status | Verification / fix inspection |
| --- | --- | --- |
| SOL-008 | PARTIALLY FIXED | Claimed CI now matches production source; both current artifact records, completed remote outcomes and fixed annotation status are present. All three earlier focused consistency/rejection tests pass. The remaining summary/count/provenance agreement is still not satisfied. |

SOL-001/002/003/004/005/006/007/009/010/012/013 remain verified fixed through
their protected contracts and applicable gates. No new production regression
was found in this evidence-only remediation.

## SOL-008 — Final contract evidence is not reconciled

Severity: **Medium**.

Disposition: **BLOCKER**.

Related AC: **AC-027**, **AC-028**.

Location: `docs/research/phase-0.2-findings.md`, source narrative and baseline
rows in the measured performance table; `docs/research/phase-0.2-results.json`,
quality_gates and results.AC-019/023/024 evidence paths;
`docs/research/phase-0.2-remediation-rereview-3.md`, final suite/gate claims.

Problem: Refreshing baseline medians did not refresh the remaining baseline
statistics. The readable table explicitly claims medians of run p95s and traced
median peaks, but its three baseline p95s are the maxima of run medians, while
the allocation values remain from the older measurement. Current candidate rows
agree with the refreshed JSON.

| Baseline summary | Readable p95 ms | Recorded median p95 ms | Readable peak bytes | Recorded median peak bytes |
| --- | --- | --- | --- | --- |
| flat_10000/scalar_write | 25.955 | 33.651125 | 2414732 | 2463932 |
| linear_20/nested_leaf | 1.361 | 1.471375 | 71840 | 63720 |
| mixed_parent/coupled_10field | 0.504 | 0.569875 | 33480 | 33768 |

The JSON's final full-suite gate still says 147 tests and describes the two
resolved review contracts as expected blocker verification. The readable report
says 149 passing tests, while the committed suite includes the additional
fourth-review verification. The implementation report's final gate table still
has 147 tests, 22 formatted files and 33 checked Markdown files without marking
these as historical executions. This is the same previously required agreement
of the final verification record, not a demand to rewrite earlier review reports.

The readable report now names clean a360bcc as the measured commit; benchmark
metadata correctly retains the actual 7bf8383 dirty-tree measurement. Those
package hashes are identical, so current code is genuinely measured and qualified.
The narrative must explain that relationship rather than imply that the earlier
measurement was executed on a later clean commit.

Moving artifact data under artifact_qualification.lanes also left final AC proof
paths artifact_qualification.commands (AC-019/023) and
artifact_qualification.resolved_dependencies (AC-024) pointing to absent members.
The underlying lane proof is present; reconcile these trace references.

Evidence: The new test parses existing readable benchmark rows, derives medians
from their three recorded runs and compares claimed values at displayed rounding
precision. It reports exactly six baseline p95/allocation mismatches. Previous
source/hash/CI verification passes. Manual comparisons establish the remaining
count/provenance/proof-path disagreements.

Relationship to current change: **SAME UNRESOLVED SOL-008 ROOT CONTRACT**.
All these checks are part of the final P02-6 agreement required in the previous
review. No new production behavior, runtime, performance budget or architecture
requirement is added.

Why it matters: The handoff misreports latency tails, allocation costs and final
verification outcomes. Some advertised AC proof references do not resolve to
the qualifying records that are now present.

Why this blocks the current change: AC-027/028 and P02-6 require truthful
median/p95/allocation reports and final evidence mapping actual outcomes, counts,
measured source metadata and proof paths. Partially refreshing these designated
deliverables does not satisfy that release contract.

Required behavior: Finish the existing reconciliation checklist: correct all
summary statistics from the recorded runs; report executed final gate counts and
outcomes consistently (or label older runs historical); distinguish measured
dirty source from the later hash-equivalent qualified commit; point AC artifact
proofs at the present lane records. Preserve measured metadata and prior Sol and
prototype history. Correct measurements do not need another timing run.

Acceptance criteria: All previous SOL-008 tests and the new readable-summary
verification pass. Manual review finds agreement across both designated final
deliverables and the implementation report, with actual counts/outcomes and
correct measured/qualified source relationships and proof references.

Verification artifact:
`tests/test_sol_phase02_rereview_5.py::test_sol008_readable_benchmark_summaries_match_recorded_runs`,
protected earlier consistency tests and manual final-record comparisons.

Verification status: **CONFIRMED FAILING — six baseline summary mismatches**.

**ESCALATION RECOMMENDED:** SOL-008 has survived multiple attempts. Use a
stronger evidence reconciliation step that derives summaries and checks the
complete final checklist. This is not an environmental or architectural block;
another partial field refresh will not close the contract.

## Follow-ups, observations and convergence

| Follow-up | Severity | GitHub status |
| --- | --- | --- |
| SOL-011 — Repeated recursive-root after-validator invocation | Low | EXISTING ISSUE [#2](https://github.com/eddiethedean/pydandict/issues/2), verified open. |
| Previously excluded published-alpha private reporting policy | Existing plan follow-up | EXISTING ISSUE [#1](https://github.com/eddiethedean/pydandict/issues/1), verified open; outside this change. |

No new unrelated follow-up or observation was confirmed. Neither existing issue
enters remediation. No new root-cause blocker is assigned.

- Previous blockers fully resolved this iteration: **0 of 1**.
- Blockers remaining: **1**, SOL-008; CI/artifact identity and several recorded
  outcomes are now repaired, but final agreement is incomplete.
- New blockers attributable to remediation: **0**.
- New unrelated follow-ups: **0**.
- The remediation is making progress within the same single finding, but the
  loop has not converged. Only SOL-008 goes back to implementation.

## Quality gates

Local environment: CPython 3.14.3, macOS arm64, Pydantic 2.13.4,
pydantic-core 2.46.4 and Pyright 1.1.411.

| Gate actually executed / observed | Result | Classification / notes |
| --- | --- | --- |
| Complete suite before new review verification | 150 passed, 2 warnings in 100.85s | PASS; all 36 earlier protected Sol cases and actual benchmark protocol pass. |
| Complete suite including new review verification | 150 passed, 1 failed, 2 warnings in 96.89s | EXPECTED BLOCKER VERIFICATION; only the new SOL-008 summary agreement case fails. |
| Previous focused review tests plus new summary verification | 3 passed, 1 failed in 0.25s | EXPECTED BLOCKER VERIFICATION; only the new summary agreement case fails. |
| Strict positive/independent negative typing | Passed | PASS; eight files, zero unexpected errors; exactly four negative errors. |
| Public type completeness | 100% | PASS. |
| CI-scoped Ruff/format before new verification | Passed; 23 files formatted | PASS. |
| Docs before this review | 35 Markdown, 207 links, 8 examples; zero errors | PASS for links/examples; semantic evidence truthfulness is not checked by this script. |
| CI-scoped Ruff/format including new verification | Passed; 24 files formatted | PASS. |
| Docs including this review | 36 Markdown, 210 links, 8 examples; zero errors | PASS. |
| Final diff / protected artifact preservation | Passed | git diff --check passes; only this report and the new test are added. All production/final evidence/previous verification remain unchanged. |
| Qualifying production CI/artifacts | Passed at a360bcc | Successful run 34862206206 and both recorded artifact lane results qualify identical production/workflow/helper source. |
| Latest evidence/test commit CI | Pending | Run 34866518540 has no reported failure; no all-lane completion claim made. |
| Fresh local artifact invocation | Not run in this review | Remote qualification and recorded current lane proof used; no local execution claimed. |
| Release-only preflight/publication | Not run | Outside review. |

No production, final evidence or earlier protected verification was modified.
New local review verification has not been pushed or run remotely.

**NEEDS FIXES**
