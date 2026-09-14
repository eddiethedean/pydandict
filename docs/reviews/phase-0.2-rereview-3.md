# Sol — Phase 0.2 third production re-review

Reviewed candidate: `7bf838325c462ceef66d32a2467ffafa40f938f2` on `main`.
Review date: September 14, 2026.

The approved [Phase 0.2 contract](../phase-0.2-plan.md), its explicit non-scope,
[previous review](phase-0.2-rereview-2.md), protected verification and
[implementation report](../research/phase-0.2-remediation-final.md) remain
authoritative. The change boundary includes the Phase 0.2 implementation and its
bounded remediation; publishing, broader dependencies and unrelated follow-ups
remain excluded. Production implementation and all prior verification artifacts
were left unchanged. Only this review and two blocker regression tests were added.

## Acceptance criteria

| AC | Status | Evidence / remaining obligation |
| --- | --- | --- |
| AC-001 | VERIFIED | Annotation/runtime matrix, recursive/specialized models and both protected deferred ABC migration cases pass. |
| AC-002 | NOT SATISFIED | SOL-001: unresolved ignored ClassVar defeats deferred concrete-field audit; earlier concrete/alias/generic rejection cases pass. |
| AC-003 | VERIFIED | Closed-value, unsafe hashing, cycle, adoption and recovery contracts pass. |
| AC-004 | VERIFIED | Configuration/hooks, names/aliases and typed-extra policy contracts pass. |
| AC-005 | VERIFIED | Nominal identity, mapping/key/attribute, equality and hashing contracts pass. |
| AC-006 | VERIFIED | Coupled updates, malformed input, duplicates, no-op counters and input-callback contracts pass. |
| AC-007 | VERIFIED | Rollback/frozen/ancestor controls and failed existing-model validation preserve state and later recovery. |
| AC-008 | VERIFIED | Scalar-drift, topology and canonical-safe normalization controls pass. |
| AC-009 | VERIFIED | Public modes/strictness/aliases/context controls pass; protected SOL-012 context and strict existing-model tests pass. |
| AC-010 | VERIFIED | Adoption/retained/stale handle matrix passes; public revalidation now returns an independent root. |
| AC-011 | VERIFIED | Augmented assignment, exact-handle no-op/frozen policy and commit counters pass. |
| AC-012 | VERIFIED | Model/container iterator and failure/no-op controls pass; public revalidation preserves the source iterator. |
| AC-013 | VERIFIED | Detached removals, ancestor validation and result-preparation rollback contracts pass. |
| AC-014 | VERIFIED | Copy/deepcopy, independent nested roots, guarded conversion and bypass rejection contracts pass. |
| AC-015 | VERIFIED | Fields-set/default/cache lifecycle contracts pass; independent probe preserves source cache identity on public validation. |
| AC-016 | VERIFIED | Diagnostic categories/codes, error precedence, redaction and programming-exception controls pass. |
| AC-017 | VERIFIED | SOL-004 adapter/cache/rebuild/version/shape and reflected-access contracts pass; schema interpretation is inside _compat. |
| AC-018 | VERIFIED | Dump/JSON/schema, aliases/exclusions/context/computed/custom serialization and guard encoding controls pass. |
| AC-019 | VERIFIED | TypeAdapter/BaseModel/FastAPI request, 422 and OpenAPI controls pass locally and in clean artifact consumers. |
| AC-020 | VERIFIED | Input callback/reentry, BaseException recovery and public failed-validation isolation contracts pass. |
| AC-021 | VERIFIED | Prepared-swap/fault/disposal contracts pass; public validation no longer commits into or disposes source storage. |
| AC-022 | VERIFIED | Retained-root lifetime, graph collection and 500-replacement bookkeeping controls pass. |
| AC-023 | VERIFIED | Strict source/positive gate passes; eight files analyzed, zero errors; public completeness 100%; installed consumers verified remotely. |
| AC-024 | VERIFIED | Independent negative fixture checks exactly four required errors; verifier failure controls pass. |
| AC-025 | VERIFIED | Current committed candidate CI passed all eight runtime lanes, docs and both artifact lanes. Workflow dependencies preserve release blocking. New local blocker tests are not part of that historical green run. |
| AC-026 | VERIFIED | Current Ubuntu 3.11/3.14 artifact logs show direct/rebuilt clean external consumers, dependency/artifact records and actual typing checks. |
| AC-027 | PARTIALLY SATISFIED | Executable benchmark protocol passes, but the designated final benchmark fingerprints older production source (SOL-008). |
| AC-028 | PARTIALLY SATISFIED | Links/examples pass; final JSON/readable findings still disagree on measured candidate and verification outcomes (SOL-008). |

## Previous blockers

| Finding | Status | Verification / root-cause inspection |
| --- | --- | --- |
| SOL-001 | PARTIALLY FIXED | Protected deferred field/extra ABC positives and simple concrete negatives pass; the new unrelated-ClassVar case still lets a concrete field escape. |
| SOL-004 | VERIFIED FIXED | Reflected/direct schema-access contract passes. _compat owns namespace retrieval, checked traversal and schema wrapping; core applies annotation policy through that API. |
| SOL-008 | PARTIALLY FIXED | Current source hashes and a successful same-production-source CI reference were recorded. Actual final benchmark/artifact/readable evidence remains unreconciled. |
| SOL-013 | VERIFIED FIXED | Both protected strict/isolation/failure cases pass. Existing-model inputs are cloned before user validation and installed into a new root; independent cache/metadata/handle probe passes. |

Earlier fixed SOL-002/003/005/006/007/009/010/012 remain verified fixed through
their protected contracts, full suite and the applicable gate inspection. No new
finding ID is assigned to either surviving root cause.

## SOL-001 — Completed annotation envelope is not enforced

Severity: **High**. Disposition: **BLOCKER**. Related AC: **AC-002**.

Location: `src/pydandict/_core.py:359–394`, `_audit_incomplete_field`;
`_core.py:343–349`, unresolved annotation fallback.

Problem: Deferred declaration resolution uses whole-model typing.get_type_hints.
An unrelated unresolved ClassVar makes that operation raise NameError. The
exception is swallowed into an empty annotation map, then an unresolved field
ForwardRef is passed to a checker that deliberately defers unresolved references.
Pydantic has already compiled the concrete mutable field into the parent's
schema, so an instance can escape without ever enforcing its resolved declaration.

Evidence: Define a child with an ignored ClassVar referring to NotDefined and
numbers referring to Later; bind Later to list[int] before defining its parent.
Parent(child={"numbers": [1]}) succeeds, yielding an OwnedList. The new regression
requires the approved unsupported_annotation diagnostic and fails with
**DID NOT RAISE TypeError**. The ordinary concrete negative and deferred ABC
positive controls still pass. ClassVars are explicitly exempt from the stored
field annotation ban, so their unresolved metadata cannot excuse skipping a
resolved stored field.

Relationship to current change: **SAME UNRESOLVED SOL-001 AUDIT INVARIANT**;
this is a remaining bypass in the latest declaration-resolution remediation.

Why it matters: The declared concrete list API promises operations the owned ABC
does not provide. An unrelated ignored annotation silently changes enforcement.

Why this blocks the current change: AC-002 explicitly requires concrete mutable
declarations, including deferred completion, to fail before instance escape.
The required behavior stays within the approved annotation envelope.

Required behavior: Check the resolved stored declaration even when unrelated
ignored annotations cannot resolve. Preserve supported deferred ABCs, typed extras,
aliases and specialized generics; do not replace this bypass with blanket mutable
core-node rejection.

Acceptance criteria: The new rejection case and all previous SOL-001 positive and
negative contracts pass; no unresolved irrelevant ClassVar can disable a completed
stored-field audit.

Verification artifact:
`tests/test_sol_phase02_rereview_3.py::test_sol001_unresolved_ignored_classvar_cannot_bypass_deferred_field_audit`.
Verification status: **CONFIRMED FAILING — missing required TypeError**.

**ESCALATION RECOMMENDED:** SOL-001 has survived multiple attempts. Stronger
declaration-resolution implementation is warranted; whole-model resolution plus
an unchecked unresolved fallback is insufficient. The approved ownership
architecture does not need replacement.

## SOL-008 — Final contract evidence is not reconciled

Severity: **Medium**. Disposition: **BLOCKER**.
Related AC: **AC-027**, **AC-028**.

Location: `docs/research/phase-0.2-results.json`, benchmark.sources.candidate,
source, artifact_qualification and remaining_verification;
`docs/research/phase-0.2-findings.md:12–18`, `:99`, `:122–132`;
latest implementation report's SOL-008 entry.

Problem: Only the outer source/CI fields and suite count were refreshed. The final
benchmark still records the dirty 1123702 candidate and hashes of earlier
_compat/_containers/_core code. The outer source and readable findings identify
clean e00b52f as the measured implementation. Its latency table therefore describes
a different implementation than the document claims. Artifact qualification still
contains the earlier macOS/Python 3.11.14 record; remaining_verification says
current remote CI has not executed, despite the recorded successful run.
The readable AC trace still marks all implementation obligations locally passing,
including the open annotation invariant, and calls artifact/CI results remote
pending while the leading text points to completed CI.

Evidence: The new test compares benchmark candidate package hashes with final
source hashes and fails for _compat.py, _containers.py and _core.py. For example,
the measured core hash starts e21393dd, while the qualified current core starts
b6e06603. The benchmark candidate is explicitly dirty at 1123702; source is clean
e00b52f. The preserved measurement timestamp is 2026-09-14T12:18:05.477511+00:00.
The newer full suite passes 147 tests and current clean artifact lanes pass, but
those executions do not make the old final measurements current proof.

Relationship to current change: **SAME UNRESOLVED FINAL-EVIDENCE REQUIREMENT**.
The previous review required manual agreement of source/benchmark/artifact/AC
identities in addition to the narrower source/truthy-CI check. Passing that check
alone does not satisfy the approved final deliverable.

Why it matters: The Phase 0.2 handoff misattributes demonstrated behavior and
measurements to the implementation being reviewed.

Why this blocks the current change: P02-6 and AC-027/028 explicitly require a
reproducible candidate benchmark and truthful final evidence mapping actual AC
results, source/artifacts and CI. This is an in-scope deliverable, not a request
for an optional benchmark budget or new optimization.

Required behavior: After production fixes, record actual candidate measurements
and qualifying artifacts with their source identities; preserve earlier records
as clearly identified history. Reconcile both designated final deliverables with
executed tests, exact dependencies, per-AC outcomes and qualifying CI. Updating
hash labels without rerunning measurements is not acceptable.

Acceptance criteria: The new benchmark/source identity contract and previous
SOL-008 contracts pass; manual review finds matching executed source, benchmark,
artifact, test/AC and readable records with no unexecuted completion claims.

Verification artifact:
`tests/test_sol_phase02_rereview_3.py::test_sol008_final_benchmark_identifies_the_qualified_candidate_source`,
plus protected earlier checks and manual final-deliverable review.
Verification status: **CONFIRMED FAILING — three production hash mismatches**.

**ESCALATION RECOMMENDED:** The repeated failure requires an evidence-generation
and reconciliation step after verification. Another outer-label or separate-report
update will not resolve this contract; no architectural scope expansion is needed.

## New blockers, follow-ups and observations

No new root-cause blocker was found. Only **SOL-001** and **SOL-008** enter
remediation. SOL-004 and SOL-013 must retain their protected verification.

| Follow-up | Severity | GitHub status |
| --- | --- | --- |
| SOL-011 — Repeated recursive-root after-validator invocation | Low | EXISTING ISSUE [#2](https://github.com/eddiethedean/pydandict/issues/2), verified open. |
| Previously excluded published-alpha private reporting policy | Existing plan follow-up | EXISTING ISSUE [#1](https://github.com/eddiethedean/pydandict/issues/1), verified open; outside this change. |

No new unrelated follow-up was confirmed and no follow-up failing test was added.
No additional observation enters remediation. Upstream deprecation warnings do
not change the approved dependency pins.

## Quality gates

Local verification uses CPython 3.14.3 on macOS arm64, Pydantic 2.13.4,
pydantic-core 2.46.4 and Pyright 1.1.411.

| Gate actually executed / observed | Result | Classification / notes |
| --- | --- | --- |
| Full existing suite before new verification | 147 passed, 2 warnings in 105.47s | PASS; includes original and both earlier protected re-review files and the actual comparable benchmark protocol. |
| All protected Sol files plus new verification | 33 passed, 2 failed in 93.70s | EXPECTED BLOCKER VERIFICATION; all previous protected cases passed. |
| New third-review file | 2 failed in 0.07s | EXPECTED BLOCKER VERIFICATION; missing annotation rejection and stale benchmark source identity. |
| Complete suite with new verification | 147 passed, 2 failed, 2 warnings in 96.53s | EXPECTED BLOCKER VERIFICATION; only the two new blocker contracts fail. |
| Strict source/positive and exact negative typing, tools/check_typing.py | Passed | PASS; eight files analyzed, no unexpected diagnostics; four expected negative errors verified. |
| Pyright --verifytypes pydandict --ignoreexternal | 100% completeness | PASS locally and independently in installed remote artifact consumers. |
| CI-scoped Ruff check / format after new verification | Passed; 22 files formatted | PASS; an initial unresolved-name lint error in the new fixture was corrected without suppressing the rule. |
| Documentation links / executable examples before this report | 32 Markdown, 200 links, 8 examples; zero errors | PASS; final report-inclusive rerun recorded below. |
| Documentation links / executable examples including this report | 33 Markdown, 203 links, 8 examples; zero errors | PASS. |
| Final diff / prior artifact preservation | Passed | git diff --check passes; only this review and the new test file are added. All production files and earlier verification remain unchanged. |
| Independent SOL-013 strict/adoption/cache probe | Passed | PASS; independent result, unchanged source cache/fields-set/handle and isolated subsequent writes. |
| Current remote artifact qualification | Both Ubuntu 3.11 and 3.14 jobs passed | PASS; actual completed job logs inspected through the GitHub API. |
| Current committed candidate remote CI | Success | All eight runtime lanes, docs and both artifact lanes passed. The new local failing verification has not been pushed or executed remotely. |
| Fresh local artifact-helper invocation | Not run | Current clean artifact execution was independently verified remotely; no fresh local execution claimed. |
| Release-only preflight / publication | Not run | Outside review; ordinary-push release-only preflight correctly skipped. |

Current CI is [run 34855996934](https://github.com/eddiethedean/pydandict/actions/runs/34855996934),
head 7bf8383. Both qualification records contain 25 commands, no source path
injection, external site-packages imports and four actual expected negative errors
for each direct/rebuilt artifact. Python versions are 3.11.16 and 3.14.7;
Pydantic 2.13.4, pydantic-core 2.46.4, FastAPI 0.141.1, httpx 0.28.1 and
Pyright 1.1.411 are recorded in both lanes.

| Artifact SHA-256 | Python 3.11 | Python 3.14 |
| --- | --- | --- |
| Direct wheel | c84dfe4375b91fc33df2feb9b31ef6420ca14cb48d6a38dc14e89f631922bc84 | e6604ef294603f41782a36b641f98fe97aed527ffb5565eb97488472203e4f91 |
| Rebuilt wheel | 83e0ded626a383df4a09e7271f0439ebf3799b4a53cbc6f50de063f12b0494b5 | 0e6e863a40126239c3c4cb8b0f34ddeb76d2760374892a420eebddd008f1dc0a |
| Source distribution | 6d835fe4dd7d81315c917fadc5d8317cce9bdd6d4ce5f255fcabfca1143b5ecc | eb18596adee0d146e038e28403e0b7b1a8329f6b79e142e0b4801a84ec6c0d13 |

These are review observations of executed current artifacts, not replacements
for the implementation-owned final evidence deliverables.

## Convergence

- Previous blockers resolved: **2 of the latest 4**, SOL-004 and SOL-013.
- Blockers remaining: **2**, SOL-001 and SOL-008, with stable IDs preserved.
- New blockers attributable to remediation: **0**; the new probes expose remaining
  instances of the existing annotation and evidence invariants.
- New unrelated follow-ups: **0**; existing issues #1/#2 remain outside remediation.
- The loop is shrinking from four to two, but both surviving blockers have failed
  repeated attempts. Escalate their implementation/evidence work as described above.

**NEEDS FIXES**
