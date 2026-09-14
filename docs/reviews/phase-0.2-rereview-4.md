# Sol — Phase 0.2 fourth production re-review

Reviewed candidate: `a360bcc90e4b0f9beba4c3cfd394c9bdb68b80db` on `main`.
Review date: September 14, 2026.

The [approved plan](../phase-0.2-plan.md), AC/verification matrix and explicit
non-scope remain sticky. This review covers Phase 0.2 and bounded remediation,
prioritizing the two blockers in the [third review](phase-0.2-rereview-3.md) and
the [latest implementation report](../research/phase-0.2-remediation-rereview-3.md).
No production, implementation-owned evidence, workflow or prior verification
artifact was changed. This report and one blocker verification test were added.

## Acceptance criteria

| AC | Status | Verification |
| --- | --- | --- |
| AC-001 | VERIFIED | Supported annotation/runtime matrix, recursive/generic fixtures and deferred ABC migration contracts pass. |
| AC-002 | VERIFIED | SOL-001 field-local resolution fixes the ClassVar bypass; all prior alias, deferred concrete field/extra and generic rejection contracts pass. |
| AC-003 | VERIFIED | Closed-value/cycle/hash-position/adoption boundary and rollback controls pass. |
| AC-004 | VERIFIED | Configuration, hooks, names/aliases and typed-extra policy matrix passes. |
| AC-005 | VERIFIED | Nominal BaseModel/mapping identity, ordering, reads, equality and hashing controls pass. |
| AC-006 | VERIFIED | Atomic coupled update, malformed/generator input, duplicates and no-op counters pass. |
| AC-007 | VERIFIED | Ancestor/frozen/rollback/recovery controls and failed public revalidation isolation pass. |
| AC-008 | VERIFIED | Scalar drift, retained topology and canonical-safe normalization controls pass. |
| AC-009 | VERIFIED | Public mode/alias/strictness/context matrix and protected SOL-012/013 controls pass. |
| AC-010 | VERIFIED | Detached adoption, repeated inputs, retained/reordered/stale handles and public existing-model isolation pass. |
| AC-011 | VERIFIED | Augmented assignment and identity/frozen-policy/commit-count contracts pass. |
| AC-012 | VERIFIED | Model-local/container-root iterator, no-op/failure and source revalidation iterator controls pass. |
| AC-013 | VERIFIED | Detached removal results, ancestor validity and preparation-failure rollback controls pass. |
| AC-014 | VERIFIED | Model/guard copy and deepcopy ownership, conversion and trusted-bypass rejection controls pass. |
| AC-015 | VERIFIED | Fields-set/default/reset/cache metadata lifecycle controls pass. |
| AC-016 | VERIFIED | Diagnostic prefixes/categories, error precedence, redaction and programming-exception propagation pass. |
| AC-017 | VERIFIED | Adapter version/shape/cache/rebuild controls and direct/reflected schema-access verification pass. |
| AC-018 | VERIFIED | Serializer/dump/schema/alias/exclusion/context/computed-field and guarded encoding controls pass. |
| AC-019 | VERIFIED | TypeAdapter/BaseModel/FastAPI request, 422 and OpenAPI checks pass locally and in both current artifact lanes. |
| AC-020 | VERIFIED | Same-root callbacks, reentry, BaseException recovery and failed public validation isolation pass. |
| AC-021 | VERIFIED | Prepared-swap/fault/guarded disposal contracts pass; public validation stays detached. |
| AC-022 | VERIFIED | Retained-root lifetime, graph collection and 500-replacement bookkeeping controls pass. |
| AC-023 | VERIFIED | Strict eight-file positive proof and 100% public completeness pass locally and in installed consumers. |
| AC-024 | VERIFIED | Exact independent four-error negative fixture and verifier failure controls pass. |
| AC-025 | VERIFIED | Candidate CI succeeded in all eight runtime lanes, docs and both artifact lanes; reusable release check/build/publish dependencies remain enforced. |
| AC-026 | VERIFIED | Current Ubuntu 3.11/3.14 direct/rebuilt wheel consumers, external imports, Twine, dependencies and artifact hashes verified from actual job logs. |
| AC-027 | PARTIALLY SATISFIED | Refreshed JSON has complete current-source benchmark protocol; readable comparison retains baseline values from the earlier environment (SOL-008). |
| AC-028 | NOT SATISFIED | SOL-008: designated final source/CI/artifact/AC/test outcomes and readable findings remain inconsistent despite completed qualifying CI. |

## Previous blockers

| Finding | Status | Verification / root cause |
| --- | --- | --- |
| SOL-001 | VERIFIED FIXED | Target-only get_type_hints resolution prevents unrelated ClassVar failure from skipping the stored declaration. Protected regression passes; independent field/extra concrete negatives and ABC acceptance/handle-retention probes all pass. |
| SOL-008 | PARTIALLY FIXED | Refreshed benchmark candidate hashes match current package source. Claimed CI still identifies different production code, old artifact data remain designated final, and readable outcomes contradict passing tests/current CI. New verification confirms the false CI identity. |

All earlier fixed SOL-002/003/004/005/006/007/009/010/012/013 remain verified fixed
through protected tests, complete runtime verification and relevant gate/fix
inspection. No new substantive production regression was confirmed.

## SOL-008 — Final contract evidence is not reconciled

Severity: **Medium**.

Disposition: **BLOCKER**.

Related AC: **AC-027**, **AC-028**.

Location: `docs/research/phase-0.2-results.json`, ci.current_candidate_run,
artifact_qualification, quality_gates, results.AC-025/026 and
remaining_verification; `docs/research/phase-0.2-findings.md:18–39`, `:83–89`,
`:105`, `:128–145`; latest implementation report's SOL-008 limitation.

Problem: Benchmark/source identity is now correct, but final evidence still
claims e00b52f CI applies to the current tree. That commit has different production
_core.py code. The required final artifact record remains the old macOS/Python
3.11.14 qualification. JSON AC-025/026 and remaining_verification say current
remote lanes have not executed. Readable findings call the fix unpushed, say the
two blocker tests fail, and classify the already fixed annotation AC as BLOCKED.
These statements are not accurate descriptions of the committed candidate.

The readable benchmark table refreshes candidate values but retains old baseline
values while describing both sides as measured under the same environment. The
current JSON baseline median is 24.8954165 ms for flat_10000/scalar_write,
1.326958 ms for linear_20/nested_leaf and 0.4984585 ms for the mixed ten-field
batch; the readable table still gives 24.491, 1.232 and 0.490 ms respectively.

Evidence: The new verification reads package files from the claimed CI commit
using git show and compares their hashes with the final source record. It fails
on pydandict/_core.py: claimed CI code hashes to b6e06603..., current measured
code hashes to b878b477.... Existing source/benchmark identity checks pass.

Actual candidate CI is successful [run 34862206206](https://github.com/eddiethedean/pydandict/actions/runs/34862206206),
head a360bcc. Both current Ubuntu artifact logs contain 25 actual commands,
external direct/rebuilt site-packages imports, no source-path injection and four
expected negative typing errors per artifact. The implementation report's
missing local pip/twine does not prevent recording this already executed proof.

Relationship to current change: **SAME UNRESOLVED FINAL-EVIDENCE REQUIREMENT**.
The approved P02-6 deliverables and previous SOL-008 manual acceptance contract
already required source/benchmark/artifact/CI/AC agreement. No new architecture,
performance ceiling, consumer environment or public API is requested.

Why it matters: The next phase receives contradictory verification outcomes and
a CI claim attached to a different implementation. The readable comparison
misattributes baseline measurements to the refreshed environment.

Why this blocks the current change: AC-027/028 and P02-6 require truthful measured
comparisons and final evidence mapping actual commands, test/AC outcomes, source
and artifact identities, dependencies and qualifying CI URLs. Required evidence
cannot claim different-source CI or label already executed proof unavailable.

Required behavior: Finish reconciling both designated final deliverables with the
current source and executed tests/CI/artifacts. Refresh all readable benchmark
rows from the same recorded run; identify older qualification as historical if
retained. Keep the measured source's actual dirty-tree status and hashes: the
plan explicitly allows measured dirty source and does not require relabeling a
measurement with a later evidence-only commit. Preserve prior review and
prototype history; do not rerun correct measurements just to change commit labels.

Acceptance criteria: All previous SOL-008 checks and the new CI/source identity
verification pass. Manual review confirms correct test counts, passing SOL-001
outcomes, current qualifying CI/artifacts/dependencies, complete AC trace and
readable benchmark agreement. No unexecuted results or source relabeling.

Verification artifact:
`tests/test_sol_phase02_rereview_4.py::test_sol008_claimed_candidate_ci_qualifies_the_recorded_package_source`,
protected earlier consistency tests and manual review of the designated files.

Verification status: **CONFIRMED FAILING — claimed CI has different _core.py**.

**ESCALATION RECOMMENDED:** This blocker has survived multiple attempts. The
remaining work is evidence reconciliation after completed verification, not
specification ambiguity or absent CI access. Use a stronger implementation/evidence
generation step; another narrow label refresh will not finish the contract.

## New blockers, follow-ups and observations

New root-cause blockers: **none**. Only **SOL-008** enters remediation. Do not
reopen SOL-001 or address unrelated issues during the evidence fix.

| Follow-up | Severity | GitHub status |
| --- | --- | --- |
| SOL-011 — Repeated recursive-root after-validator invocation | Low | EXISTING ISSUE [#2](https://github.com/eddiethedean/pydandict/issues/2), verified open. |
| Previously excluded published-alpha private reporting policy | Existing plan follow-up | EXISTING ISSUE [#1](https://github.com/eddiethedean/pydandict/issues/1), verified open; outside this change. |

No new worthwhile unrelated defect was confirmed. No follow-up failing test or
new observation was added. Neither existing issue enters remediation.

## Quality gates and current artifacts

Local environment: CPython 3.14.3, macOS arm64, Pydantic 2.13.4,
pydantic-core 2.46.4 and Pyright 1.1.411.

| Gate actually executed / observed | Result | Classification / notes |
| --- | --- | --- |
| Complete suite before new review verification | 149 passed, 2 warnings in 95.25s | PASS; all 35 earlier protected Sol cases and actual benchmark protocol pass. |
| Complete suite including new review verification | 149 passed, 1 failed, 2 warnings in 96.30s | EXPECTED BLOCKER VERIFICATION; only the new SOL-008 CI/source identity test fails. |
| Previous third-review file plus new verification | 2 passed, 1 failed in 0.20s | EXPECTED BLOCKER VERIFICATION; both previous regressions now pass, new false-CI-identity case fails. |
| Independent SOL-001 probes | All four pass | PASS; deferred concrete rejection and ABC acceptance/handle retention for fields and typed extras with an unresolved ClassVar. |
| Strict source/positive and exact negative typing | Passed | PASS; eight positive files with zero errors, independent fixture with four exact errors. |
| Public Pyright completeness | 100% | PASS locally and in both installed artifact lanes. |
| CI-scoped Ruff check / format before new verification | Passed; 22 files formatted | PASS; final review-inclusive check recorded below. |
| Docs before this review | 34 Markdown, 204 local links, 8 examples; zero errors | PASS for links/examples; this structural gate does not verify prose/evidence truthfulness. |
| CI-scoped Ruff check / format including new review verification | Passed; 23 files formatted | PASS. |
| Docs including this review | 35 Markdown, 207 local links, 8 examples; zero errors | PASS. |
| Final diff and protected artifact preservation | Passed | git diff --check passes; only this report and the new test file are added. No production/evidence/previous verification changes. |
| Current candidate remote CI | All required jobs successful | PASS, run 34862206206 on a360bcc; eight runtime lanes, docs and both artifact lanes. |
| Current clean artifact job logs | Both inspected | PASS; direct/rebuilt external imports, Twine, runtime/HTTP/typing consumers and exact dependency/hash records verified. |
| Fresh local artifact invocation | Not run in this review | Remote current-source qualification was verified instead; no local execution claimed. |
| Release-only preflight/publication | Not run | Outside review; release-only preflight correctly skipped on the ordinary push. |

Both artifact environments record Pydantic 2.13.4, pydantic-core 2.46.4,
FastAPI 0.141.1, Starlette 1.6.0, httpx 0.28.1 and Pyright 1.1.411.
Python versions are 3.11.16 and 3.14.7 on Linux x86_64.

| SHA-256 | Python 3.11 | Python 3.14 |
| --- | --- | --- |
| Direct wheel | 0fd36d6d577f9d08a03b256ce318a7eace7142c282b304757287766f2cdee169 | e95600f75143b428fb3c958f4aeb28aec694fd4be66f5cff428309dafc952272 |
| Rebuilt wheel | 7a8e03fa4120c278cdd8d45ae70620bf5b72fc6fce3c75c4865ce11123c3096f | 6b78f4637ac335afd0e73c7252d0887a569da8e274f41a08e5d6fe3fda4ab063 |
| Source distribution | 8fe82250c8abc5b49ccdd8dadf9a152b10b9c02152e5b894be79a8fcac7bed67 | 52e2d1c12f24c73b62c06da0230513880e6225937520650251bac5d782c1dc79 |

These are reviewer observations of current executed artifacts. They do not
replace the implementation-owned final evidence deliverables.

## Convergence

- Previous blockers resolved: **1 of 2**, SOL-001.
- Blockers remaining: **1**, SOL-008, preserving its stable ID.
- New blockers attributable to remediation: **0**; no substantive production
  regression confirmed.
- New unrelated follow-ups: **0**; existing issues #1/#2 remain separate.
- The loop converges from two blockers to one. Benchmark identity is repaired
  and current CI/artifacts pass; finish final evidence reconciliation rather
  than expanding implementation scope.

**NEEDS FIXES**
