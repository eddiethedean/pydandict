# Sol — Phase 0.2 second production re-review

Reviewed candidate: `8560c5b31863e29eaf3f740784b0db06e85e1b23` on `main`.
Review date: September 14, 2026. Approved contract:
[Phase 0.2 plan](../phase-0.2-plan.md), committed at `0df17e2`.
Production baseline: `07fec9b7eafef5b00befe9fa24ccd012ce0232a1`.
Original implementation: `83ce43f` / `1123702`; remediation: `1cb73e0`, followed
by the documentation-only `8560c5b`.

The approved scope and non-scope remain unchanged. This review read the plan,
the [original review](phase-0.2-review.md), the
[first re-review](phase-0.2-rereview.md), their verification artifacts, the
implementation evidence and the [latest remediation report](../research/phase-0.2-remediation-latest.md).
Production implementation, configuration, workflows and prior review artifacts
were not modified. New verification is limited to four release blockers.

The original 141-test suite passes. The eight first-re-review contracts now pass.
Six additional cases fail for the expected reasons. CI qualification is verified;
its success does not cover these newly demonstrated contract regressions.

## Acceptance criteria

VERIFIED applies to the bounded contract and the evidence below, not arbitrary
trusted callbacks or repository-wide perfection. Regressions introduced by the
existing-model validation branch share SOL-013 rather than separate symptom IDs.

| AC | Status | Verification / remaining gap |
| --- | --- | --- |
| AC-001 | REGRESSED | SOL-001: supported deferred nested ABC fields and typed extras now fail construction. Other scalar, aggregate, generic and recursive fixtures pass. |
| AC-002 | PARTIALLY SATISFIED | Original and first-re-review concrete/alias/generic rejection cases pass, but the required supported ABC migration rejects under deferred parent completion (SOL-001). |
| AC-003 | VERIFIED | All original hash-position, direct ingress, setdefault/pair-update, cycle, output-value and timezone controls pass. SOL-002 fix inspected. |
| AC-004 | VERIFIED | Config/default/revalidation/hook/namespace and extra-policy fixtures pass. Annotation completion remains AC-001/002. |
| AC-005 | VERIFIED | Nominal model/mapping identity, canonical keys/order, equality and mutable/frozen hashing fixtures pass. Public input ownership is AC-010. |
| AC-006 | VERIFIED | Complete batch, duplicates/kwargs/self-update, late input failures and no-op counters pass; slice and mapping input callbacks now run under the guard. |
| AC-007 | REGRESSED | Ordinary transaction rollback/frozen-ancestor controls pass, but a failing public validator can commit an edit into its existing input root (SOL-013). |
| AC-008 | VERIFIED | Canonical untouched drift, topology rejection, supported normalizers and stateful controls pass. |
| AC-009 | REGRESSED | SOL-012 supplied-context contract passes; SOL-013 now rejects a valid existing ABC model with strict=True, unlike the pinned control. Other mode/alias/context controls pass. |
| AC-010 | REGRESSED | SOL-013 returns the existing input root, replaces/stales its saved handles, and permits result edits to change the input. Other adoption/reorder/replacement fixtures pass. |
| AC-011 | VERIFIED | Exact model/guard identity no-ops, augmented assignments and frozen-ancestor checks pass; SOL-003 remains fixed. |
| AC-012 | REGRESSED | Normal iterator controls pass. SOL-013's failed public validation changes the source and invalidates its saved iterator. |
| AC-013 | VERIFIED | Detached pop/popitem returns and result-preparation recovery tests pass. |
| AC-014 | VERIFIED | Canonical model/guard copies, deep/shallow conversion, frozen-source updates and trusted-path rejection tests pass. |
| AC-015 | REGRESSED | Reset/default/fields-set and ordinary failure-cache tests pass. SOL-013 discards an existing input's cached computed value during public validation without a source edit. |
| AC-016 | VERIFIED | Unsafe insertion now has the required prefix; exact policy/error precedence and unchanged programming-exception controls pass. |
| AC-017 | REGRESSED | SOL-004: the new annotation audit reads/interprets raw core schema outside the checked adapter. Other shape/version/cache/rebuild controls remain green. |
| AC-018 | VERIFIED | Supported raw-snapshot dumps, aliases, exclusions, contexts, computed/custom serialization, schema metadata and direct guard-encoding controls pass. |
| AC-019 | VERIFIED | Source and clean-artifact TypeAdapter/BaseModel/FastAPI request/422/OpenAPI controls pass; existing-model ownership is tracked under SOL-013. |
| AC-020 | REGRESSED | SOL-010 input materialization is fixed. SOL-013 instead passes live guards to public validators and commits into an existing root outside its transaction guard. |
| AC-021 | REGRESSED | All original swap/fault/disposal controls pass, but SOL-013 disposes the live input's old computed cache while busy=False during public validation. |
| AC-022 | VERIFIED | Root lifetime, collection and 500-replacement/bounded-current-node controls pass. |
| AC-023 | VERIFIED | Independent strict Pyright 1.1.411: eight files, zero diagnostics; public completeness 100%; installed consumer gates also passed in both Ubuntu lanes. |
| AC-024 | VERIFIED | Actual independent negative fixture and exact four-error multiset/failure controls pass. |
| AC-025 | VERIFIED | Candidate CI passed all eight required runtime lanes, both artifact lanes and docs; reusable release needs chain remains enforced. Release-only preflight was correctly skipped on this ordinary push. |
| AC-026 | VERIFIED | Both Ubuntu 3.11/3.14 logs record direct/rebuilt clean consumers, external imports, four negative errors per artifact, hashes and resolved dependencies. |
| AC-027 | PARTIALLY SATISFIED | Actual baseline/current-source benchmark execution passes the complete protocol, but the durable final evidence still identifies the earlier measured source (SOL-008). No speed/budget claim is required. |
| AC-028 | PARTIALLY SATISFIED | Links/examples pass and latest Markdown reports current CI, but the required final JSON/readable findings retain stale source, counts, remote-pending results and completion claims (SOL-008). |

## Previous blockers

| Finding | Status | Verification / fix inspection |
| --- | --- | --- |
| SOL-001 | PARTIALLY FIXED | All previous rejection cases pass. New field and typed-extra ABC controls fail because the resolved-schema audit cannot distinguish supported ABCs from concrete list nodes. Remediation introduced this regression. |
| SOL-002 | VERIFIED FIXED | Original/direct-ingress and both first-re-review insertion cases pass. setdefault and pair-update check hash-position safety before native hashing. |
| SOL-003 | VERIFIED FIXED | Original identity/frozen-ancestor contracts and related assignment controls pass. |
| SOL-004 | REGRESSED | Original cache/shape/static controls and adapter tests pass; new getattr-based raw schema access bypasses their limited AST check and the required boundary. |
| SOL-005 | VERIFIED FIXED | Actual eight-file strict run, four-error negative gate and verifier failure controls pass. |
| SOL-006 | VERIFIED FIXED | Current candidate CI and both Ubuntu clean-artifact logs verified; production package consumers genuinely ran. |
| SOL-007 | VERIFIED FIXED | Actual unmodified-baseline/current-source comparison executes successfully. Required shape/sample/correctness/count/allocation protocol and generator inspected; final evidence refresh is SOL-008. |
| SOL-008 | PARTIALLY FIXED | Required files exist and latest Markdown has current CI, but the designated final evidence and readable findings were not reconciled. New consistency test fails. |
| SOL-009 | VERIFIED FIXED | Protected disposal contract and all prepared-swap/fault/recovery/lifetime controls pass for normal transactions. Newly added public live-commit behavior is SOL-013. |
| SOL-010 | VERIFIED FIXED | Both protected callback cases pass. Iterable consumption now occurs inside _change; reads see committed state and rejected callbacks preserve handles/iterators/recovery. |
| SOL-012 | VERIFIED FIXED | Protected raw/existing input context differential passes; public wrapper forwards supplied context and later mutation/copy retain context=None. Its remediation introduced the distinct ownership defect SOL-013. |

## SOL-001 — Completed annotation envelope is not enforced

Severity: **High**. Disposition: **BLOCKER**. Related AC: **AC-001**, **AC-002**.

Location: `src/pydandict/_core.py:355`, `:389`, `:648`.

Problem: The new incomplete-child audit rejects any compiled list/dict/set node.
Pydantic also uses list validation nodes for supported MutableSequence fields.
Resolving a deferred child's annotation to MutableSequence[int] through a parent
therefore rejects the documented supported migration. Typed-extra values fail too.

Evidence: Both new test_sol001 cases fail with unsupported_annotation pointing at
Child's list core node and advising the ABC already declared. The matched field
probe constructs and dumps successfully on unmodified 07fec9b and initial 1123702;
HEAD raises TypeError. All older rejection contracts now pass.

Relationship to current change: **REMEDIATION-CAUSED REGRESSION OF THE SAME AUDIT**.
The stable SOL-001 contract always required supported alternatives to work;
closing a bypass by rejecting safe annotations does not complete that contract.

Why it matters: Supported deferred models cannot use the prescribed migration.

Why this blocks the current change: AC-001/002 explicitly require supported ABC
fields, deferred completion and accepting the supported migration. This requires
neither new collection support nor an expanded value envelope.

Required behavior: Audit resolved declarations accurately, including nested
fields/extras, and distinguish their declared ABC from a concrete built-in.
Preserve all prior concrete/alias/generic rejection contracts.

Acceptance criteria: Both new positive cases construct, coerce and retain their
owned handle on append; all original and first-re-review SOL-001 cases pass.

Verification artifact: `tests/test_sol_phase02_rereview_2.py`, test_sol001_*;
both earlier Sol verification files remain protected and unchanged.
Verification status: **CONFIRMED FAILING — 2 cases, expected false rejection**.

**ESCALATION RECOMMENDED:** SOL-001 has survived more than one implementation
attempt. Reconsider how completed declaration metadata is obtained within the
approved adapter; a core-node type alone cannot distinguish these declarations.
The full-root/ABC ownership architecture does not need replacement.

## SOL-004 — Compatibility boundary is bypassed again

Severity: **Medium**. Disposition: **BLOCKER**. Related AC: **AC-017**.

Location: `src/pydandict/_core.py:355–401`, `:648`.

Problem: finish now fetches __pydantic_core_schema__ with unchecked getattr and
the two core helpers interpret model/schema/type/cls keys directly. Those private
formats belong behind the single checked compatibility boundary. The original AST
contract caught object slot access/compilation but did not catch this getattr path.

Evidence: The new architecture contract reports exactly ('_core.py', 648).
Manual inspection confirms that raw schema interpretation is also outside
_compat. The prior AST, cache/rebuild and compatibility-shape cases still pass.

Relationship to current change: **REMEDIATION-CAUSED REGRESSION** of the original
SOL-004 boundary, not a new preferred-file-layout requirement.

Why it matters: Required private structure checks and schema interpretation are
no longer auditable through one version-sensitive interface.

Why this blocks the current change: AC-017 and the plan explicitly require all
raw core-schema access/inspection behind that boundary. Passing typing does not
replace the architectural acceptance criterion.

Required behavior: Delegate completed nested annotation/schema inspection through
the checked compatibility adapter. Public field/key policy may remain in core.

Acceptance criteria: New raw-access contract and prior SOL-004 contracts pass;
manual review confirms schema-shape inspection remains behind the adapter.
Coordinate with SOL-001 without introducing a second unchecked parser.

Verification artifact: `tests/test_sol_phase02_rereview_2.py`, test_sol004_*;
existing original/adapter fixtures remain unchanged.
Verification status: **CONFIRMED FAILING — 1 architecture case**.

## SOL-008 — Final contract evidence is not reconciled

Severity: **Medium**. Disposition: **BLOCKER**. Related AC: **AC-027**, **AC-028**.

Location: `docs/research/phase-0.2-results.json:8129`, `:8177`, `:8276`, `:8636`;
`docs/research/phase-0.2-findings.md`; latest remediation report's SOL-008 entry.

Problem: Adding a new Markdown remediation report did not refresh the two final
deliverables explicitly required by P02-6. The JSON still has current_candidate_run
null, 133 tests, remote matrix NOT RUN and hashes for the prior implementation.
Its 28-row completion trace and readable findings still present that earlier
evidence as the final contract record. Historical results are valid history, but
the newer report does not reconcile the designated final record.

Evidence: New consistency verification finds both source-hash mismatch and absent
current CI. _compat, _containers and _core hashes differ. The readable findings
still say current candidate CI is pending and the final suite contains 133 tests.
Actual candidate CI is green at 8560c5b; current original suite has 141 tests.

Relationship to current change: **SAME UNRESOLVED FINAL-EVIDENCE REQUIREMENT**.
No prototype records or previous Sol reports should be rewritten.

Why it matters: Users and the next phase cannot trace the candidate's demonstrated
contract and benchmark/artifact identities through the required final evidence.

Why this blocks the current change: AC-028 and P02-6 require actual per-AC outcomes,
current measured source hashes, commands/counts and qualifying CI URLs in these
deliverables. A final evidence file cannot identify a different measured source.

Required behavior: After production remediation, reconcile the final JSON and
readable findings with actual current tests, source, benchmark/artifact records,
CI and per-AC results. Clearly preserve older measurements as historical records.

Acceptance criteria: New source/CI consistency case passes; manual review verifies
all 28 AC results, source/benchmark/artifact identities and readable findings agree
with executed verification. Do not insert unexecuted outcomes to satisfy the test.

Verification artifact: `tests/test_sol_phase02_rereview_2.py`, test_sol008_*;
original presence case, docs gate and final evidence review.
Verification status: **CONFIRMED FAILING — 1 consistency case**.

**ESCALATION RECOMMENDED:** This blocker has survived multiple implementation
attempts. The issue is updating the authoritative deliverables after verification,
not missing GitHub access or specification ambiguity. Another report-only change
will not resolve the protected contract.

## SOL-013 — Public existing-model validation operates on the live input root

Severity: **High**. Disposition: **BLOCKER**.
Related AC: **AC-007**, **AC-009**, **AC-010**, **AC-012**, **AC-015**,
**AC-020**, **AC-021**.

Location: `src/pydandict/_core.py:593`, `:656–663`.

Problem: The context fix sends _data(value), containing live owned descendants,
directly to user validation. _install_prevalidated then prepares/commits into that
input root, returns it, and sets its busy flag false. Public validation is therefore
a live mutation instead of constructing an independent owned result.

Evidence:

- Ordinary model_validate(existing) returns the same root, changes the saved list
  handle and stales it. Editing the returned result changes the original source.
  The pinned revalidate_instances=always BaseModel control returns a new instance.
- strict=True rejects an already valid model's numbers with list_type because the
  inner validator sees OwnedList rather than detached canonical Python input.
  The matched BaseModel control accepts its valid input.
- A deterministic, idempotent request-input normalizer appends a missing 2 to its
  candidate and raises ValueError. Public validation raises ValidationError, but
  the source now contains [1, 2] and its saved iterator is invalidated.
- An independent cached-computed finalizer probe records (1, False) when public
  validation discards the source's old cache: live disposal occurs outside busy.
- The detached-result/source-handle probe succeeds on both 07fec9b and 1123702;
  only HEAD reuses the source and replaces its handle. Those old versions drop
  supplied context (SOL-012), so they are not claimed to satisfy the new context
  failure test. The new failure is separately confirmed on HEAD.

Relationship to current change: **NEW REMEDIATION-CAUSED OWNERSHIP REGRESSION**.
SOL-012's context invariant is fixed. Passing it by changing input adoption and
live commit semantics introduced this distinct defect.

Why it matters: Failed validation can alter an application's existing state,
successful validation can destroy borrowed handles, and valid strict revalidation
fails. This is changed behavior at the public validation/ownership boundary.

Why this blocks the current change: It violates the existing adoption/isolation,
strict public validation and callback/guard guarantees and creates a correctness
problem in the behavior being changed. It is not a request to roll back external
callback side effects; the callback receives the library's live guard as candidate
input, so the library itself permits a source-root transaction.

Required behavior: Detach existing-model inputs before user validation, preserve
supplied public context/flags, and install the validated result as an independent
owned root. Preserve the source's state, metadata, caches, handles and iterators.
Canonical mutation/copy must still use context=None, as protected by SOL-012.

Acceptance criteria: Both new SOL-013 cases pass with strict acceptance, independent
result/source writes, unchanged source after validation failure and later recovery;
the original SOL-012 context differential remains green. No commit or disposal
should occur on the source solely because it was used as public validation input.

Verification artifact: `tests/test_sol_phase02_rereview_2.py`, test_sol013_*;
existing context, copy/adoption, callback and transaction recovery contracts.
Verification status: **CONFIRMED FAILING — 2 cases, strict rejection and source
mutation on failure**. Non-strict identity, source-handle and cache-finalizer
regressions were independently reproduced too.

## Follow-ups

| Finding | Severity | GitHub status |
| --- | --- | --- |
| SOL-011 — Repeated recursive-root after-validator invocation | Low | EXISTING ISSUE [#2](https://github.com/eddiethedean/pydandict/issues/2), verified open; prior evidence and disposition retained. |
| Previously excluded published-alpha security/private reporting policy | Existing plan follow-up | EXISTING ISSUE [#1](https://github.com/eddiethedean/pydandict/issues/1); untouched and outside this change. |

No new unrelated follow-up was confirmed. No follow-up failing verification was
added. Neither item enters the implementation handoff.

## Quality gates

Local environment: CPython 3.14.3, macOS 26.5.2 arm64, Pydantic 2.13.4,
pydantic-core 2.46.4, FastAPI 0.141.1, Starlette 1.6.0, httpx 0.28.1,
Pyright 1.1.411, pytest 9.1.1 and Hypothesis 6.151.9.

| Gate actually executed / observed | Result | Classification / notes |
| --- | --- | --- |
| Original complete suite, before new review cases | 141 passed, 2 warnings in 168.74s | PASS; includes all 19 original Sol cases, 8 first-re-review cases and actual three-run-per-revision benchmark. |
| First-re-review protected file | 8 passed in 0.61s | PASS; all prior targeted rejection/insertion/callback/context contracts. |
| New protected review file | 6 failed in 0.88s | EXPECTED BLOCKER VERIFICATION; corrected fixture signature before confirming final failures. |
| Complete suite with new review cases | 141 passed, 6 failed, 2 warnings in 103.11s | EXPECTED BLOCKER VERIFICATION; all failures are the new six contracts; no other required runtime failure. |
| tools/check_typing.py | Passed | PASS; positive and exact negative proof. Independent Pyright JSON: 8 files, 0 errors/warnings, exit 0. |
| Pyright verifytypes pydandict --ignoreexternal | 100% | PASS locally; clean installed proof independently observed in both Ubuntu artifact jobs. |
| CI-scoped Ruff check / format | Passed; 21 files formatted | PASS after new verification added. Initial .venv/bin/ruff lookup unavailable; rerun with installed /opt/homebrew/bin/ruff passed. |
| tools/check_docs.py with all review artifacts | 31 Markdown, 200 links, 8 examples; 0 errors | PASS; an intermediate missing companion JSON link was resolved by completing that artifact, then the gate was rerun. |
| Review JSON and protected-artifact hashes | Validated | PASS; all 28 AC rows, current production identities, prior protected artifacts and new verification hash checked. |
| Candidate remote CI / artifact logs | All required jobs succeeded | PASS, observed [run 34846986132](https://github.com/eddiethedean/pydandict/actions/runs/34846986132), head 8560c5b; all 8 runtime lanes, docs and 2 Ubuntu artifact lanes. |
| Fresh local artifact-helper invocation | Not run in this re-review | Required current clean-artifact execution instead verified directly from both successful remote jobs; no claim of a fresh local invocation. |
| Release publication / release-only preflight | Not run | Outside this review; ordinary-push package preflight correctly skipped. No publication/tag performed. |

Both Ubuntu artifact records contain 25 actual commands, source_path_injection
false throughout, direct/rebuilt site-packages imports, exact resolved dependencies
and direct/rebuilt negative typing counts 4/4. Python versions are 3.11.16 and
3.14.7; FastAPI 0.141.1, Starlette 1.6.0, httpx 0.28.1, Pydantic 2.13.4,
pydantic-core 2.46.4 and Pyright 1.1.411 are recorded independently in each lane.
Artifact hashes and review-source identities accompany this review in
[the machine-readable record](phase-0.2-rereview-2-results.json).

## Observations

No additional implementation suggestion is added to the remediation loop.
Timing remains observational; dependency deprecation warnings do not amend the
approved pins or create unrelated release blockers.

## Convergence and bounded handoff

- Earlier blockers verified fixed: **8 of 11** — SOL-002/003/005/006/007/009/010/012.
- Four remaining blockers: **SOL-001, SOL-004, SOL-008, SOL-013**.
- Of the latest six-blocker handoff, **4** are fixed; SOL-001/008 remain partial.
- Remediation reopened SOL-004 and introduced **1 new root-cause blocker**, SOL-013.
  It also regressed supported annotation behavior under the still-open SOL-001.
- New unrelated follow-ups: **0**; SOL-011/#2 and excluded #1 remain separate.
- The count fell from six to four, but regression-free convergence has not been
  reached. Prioritize accurate annotation resolution, public input detachment and
  authoritative evidence generation; no repository-wide redesign is requested.

Only **SOL-001/004/008/013** enter remediation. Preserve every prior Sol verification
artifact and the new contracts. Do not address SOL-011/#2 or excluded follow-ups
as part of this handoff.

**NEEDS FIXES**
