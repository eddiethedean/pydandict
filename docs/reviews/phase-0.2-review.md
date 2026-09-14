# Sol — Phase 0.2 production code review

Verdict: **NEEDS FIXES**.

Reviewed production HEAD: `1123702ed080e09e00e9dee1392dcebff62e41a9`.
Approved contract: `docs/phase-0.2-plan.md`, committed at `0df17e2`.
Implementation boundary: `83ce43f` plus the README change at `1123702`.
Approved benchmark baseline: `07fec9b`. Review performed September 14, 2026 UTC.

The full approved Phase 0.2 scope remains applicable. The initial implementation
report disclosed incomplete qualification and contract coverage; that disclosure
does not amend the approved acceptance criteria. No previous Sol blocker history
was found. Production implementation was not modified. The review adds only this
report and `tests/test_sol_phase02_blockers.py` on the current branch.

The existing 93 tests pass. Nineteen additional verification cases fail for the
expected blocker reasons. There are nine root-cause findings, all in scope.
No unrelated discovery has been added to the remediation contract.

## Acceptance criteria

VERIFIED means the reviewed implementation, existing tests and independent probes
support the required behavior. It does not assert exhaustive testing of arbitrary
trusted callbacks. Partial and unsatisfied criteria map to the blockers below.

| AC | Status | Evidence / open contract gap |
| --- | --- | --- |
| AC-001 | VERIFIED | Existing generic/construction fixtures; independent nested sequence/mapping/set, nullable, Annotated, Literal, tuple/frozenset, exact scalar, finite recursive and specialized-generic runtime matrix. |
| AC-002 | NOT SATISFIED | SOL-001: deferred concrete annotations, concrete typed-extra values and nested unbound generics escape. |
| AC-003 | NOT SATISFIED | SOL-002: model keys/set/frozenset members are accepted. Existing cycle/custom-timezone/ordinary-BaseModel rejection passes. |
| AC-004 | VERIFIED | Class configuration/hook/default/name checks inspected; existing extras, protected names and destructive-policy fixtures pass. The typed-extra annotation failure is covered by AC-002. |
| AC-005 | VERIFIED | Identity, ordered mapping views, attribute/key equivalence, declared presence, equality and frozen policy inspected against existing API fixtures. |
| AC-006 | VERIFIED | Coupled bounds/late generator fixtures; independent duplicate/kwargs precedence, self-update and validator-free empty update/reset/existing setdefault counters pass. |
| AC-007 | PARTIALLY SATISFIED | Rollback/stateful/ancestor tests pass; SOL-003 permits an identical nested field write through a frozen ancestor. |
| AC-008 | VERIFIED | Existing canonical-drift and topology rejection fixtures preserve state; checks inspected in preparation. |
| AC-009 | VERIFIED | Construction/mode fixtures; independent Python/JSON/strings context probes and strict BaseModel controls pass. Mutation and copy observe Python mode with context=None. |
| AC-010 | VERIFIED | Adoption/reorder/stale-handle fixtures and stateful oracle pass; repeated-input detachment and identity reconciliation inspected. |
| AC-011 | NOT SATISFIED | SOL-003: nested model identity assignments replace/stale the model and revalidate; frozen ancestor shortcut is incomplete. |
| AC-012 | VERIFIED | Existing mapping/view fixtures; independent creation-before-first-next, root invalidation, model-local version and permanent exhaustion probes pass for list/dict/set. |
| AC-013 | VERIFIED | Nested removal/return ownership and preparation fault fixtures pass; detached-result installation inspected. |
| AC-014 | PARTIALLY SATISFIED | Existing model copies and guard deepcopy pass; SOL-002 allows hash-position models to reach clone paths that expose uninstalled candidates. |
| AC-015 | VERIFIED | Default/reset/metadata fixtures; independent cached-computed failure/success lifecycle probe passes. Disposal timing is separately AC-021. |
| AC-016 | PARTIALLY SATISFIED | Ordinary policy/programming-exception paths pass; SOL-002 and SOL-004 miss required unsupported-value/compatibility diagnostics. |
| AC-017 | NOT SATISFIED | SOL-004: raw storage/schema/cache operations bypass adapter, rebuild retains compiled variants, incompatible schema shape is unchecked. |
| AC-018 | VERIFIED | Existing custom field/model serializer, exclusions/computed/context and framework encoding fixtures pass; snapshot dispatch and direct guard encoding inspected. |
| AC-019 | VERIFIED | Source integration tests exercise TypeAdapter, BaseModel envelope, real FastAPI success/422/OpenAPI and guarded mutations. Artifact qualification is separately AC-026. |
| AC-020 | VERIFIED | Existing late-generator/reentry/fault fixtures; independent KeyboardInterrupt injections at every swap release busy guard and both ContextVars, followed by valid recovery. |
| AC-021 | PARTIALLY SATISFIED | All 60 before/after swap fault probes pass; SOL-009 cache finalization happens after busy guard release. |
| AC-022 | VERIFIED | Existing root lifetime fixtures; independent 500 replacements collect discarded handles and current node bookkeeping equals reachable nodes. |
| AC-023 | PARTIALLY SATISFIED | Actual strict run and editable-package verifytypes pass at 100%; SOL-004 private control flow remains Any-based and SOL-005 coverage verifier accepts incomplete runs; installed-artifact proof missing under SOL-006. |
| AC-024 | PARTIALLY SATISFIED | Actual four negative errors pass; SOL-005 verifier also accepts unexpected duplicate/unruled diagnostics. |
| AC-025 | PARTIALLY SATISFIED | Eight lanes and release needs chain exist and CI passes; SOL-006 required artifact proof is incomplete, so passing CI does not establish all required consumers. |
| AC-026 | NOT SATISFIED | SOL-006: only direct wheel receives consumers; isolation/negative/completeness/dependency evidence incomplete. |
| AC-027 | NOT SATISFIED | SOL-007: wrong baseline and incomplete measurement protocol/workloads/metadata. |
| AC-028 | NOT SATISFIED | SOL-008: required evidence files absent; target contract/decision documentation remains unfinished. |

## Previous blockers

None. This is the first independent review of this implementation.

## SOL-001 — Completed annotation envelope is not enforced

Severity: **High**. Disposition: **BLOCKER**.
Related AC: **AC-002**.

Location: `src/pydandict/_core.py:185`, `:480`, `:602`.

Problem: Annotation checking runs at initial subclass setup, skips unresolved
forward references and does not audit typed-extra value annotations. Nested
unspecialized generic validation is exempted while `_BUILDING` is active.

Evidence: A deferred field resolved to `list[int]` constructs successfully after
`model_rebuild`; `dict[str, list[int]]` typed extras accept a list value; an
`Envelope` field annotated with unspecialized `Box` accepts a mutable payload.
All three corresponding verification tests fail because no TypeError is raised.

Relationship to current change: Phase 0.2 explicitly introduces the completed-schema
annotation audit and explicit generic specialization contract.

Why it matters: The public annotation/runtime agreement and supported migration
boundary can be bypassed through normal supported construction APIs.

Why this blocks the current change: It directly violates AC-002's requirement that
these instances fail before escape.

Required behavior: Recursively audit completed annotations, including deferred and
typed-extra values; reject unbound generic construction at every nesting level.
Do not reject the storage wrapper `dict[str, V]` merely for being Pydantic's typed
extra wrapper; audit V. Supported ABC and explicitly specialized alternatives work.

Acceptance criteria: All SOL-001 tests pass with the leading unsupported-annotation
TypeError and migration hint where applicable; supported recursive/generic fixtures
continue to pass. Rebuild and first construction cannot bypass the audit.

Verification artifact: `tests/test_sol_phase02_blockers.py`, `test_sol001_*`.
Verification status: **CONFIRMED FAILING — 3 cases, expected missing rejection**.

## SOL-002 — Unsafe models are accepted in hash positions

Severity: **High**. Disposition: **BLOCKER**.
Related AC: **AC-003**, **AC-014**, **AC-016**.

Location: `src/pydandict/_core.py:87`, `:115`, `:120`, `:124`, `:376`.

Problem: Graph cloning checks value types without checking hash-position safety.
Frozen/hashable DictModels are cloned as mapping keys and set/frozenset members.
Some membership preparation paths clone models into internal blank candidates.

Evidence: Assigning `{Key(number=1): 1}`, `{Key(number=1)}` or its frozenset form to
an Any field succeeds. Dumping an accepted key graph can subsequently fail with
PydanticSerializationError because its snapshot key serializes as an unhashable
dict. The three mutator verification cases fail at the required rejection.

Relationship to current change: The approved ownership envelope explicitly excludes
DictModels and owned guards from hash positions, including frozen models.

Why it matters: Invalid graphs commit instead of remaining usable and unchanged;
later serialization or public use encounters invalid snapshot/model state.

Why this blocks the current change: It violates the in-scope value boundary and
atomic rejection guarantee, rather than being a request to support additional keys.

Required behavior: Validate keys/members recursively as immutable safe leaves,
tuples and frozensets only. Reject models/guards on input and validator output,
including copy/update paths, before commit with unsupported-value TypeError.

Acceptance criteria: SOL-002 tests pass, preserve values/fields-set/old handles,
and allow subsequent valid mutation. Safe aggregate keys/members remain supported;
no blank model escapes through detached graph operations.

Verification artifact: `tests/test_sol_phase02_blockers.py`, `test_sol002_*`.
Verification status: **CONFIRMED FAILING — 3 hash-position cases**.

## SOL-003 — Identity assignment is incomplete and bypasses ancestor policy

Severity: **High**. Disposition: **BLOCKER**.
Related AC: **AC-007**, **AC-011**.

Location: `src/pydandict/_containers.py:86`, `:193`;
`src/pydandict/_core.py:880`.

Problem: Sequence/mapping single-slot identity shortcuts recognize owned guards
but omit DictModel values. Model field shortcuts check local write policy without
checking frozen ancestors.

Evidence: Assigning `children[0] = children[0]` or `table['first'] = table['first']`
replaces the child and stales the saved model. Assigning a child model's current
numbers handle back to that field under a frozen parent succeeds instead of
raising frozen_instance. Three focused tests fail for these exact reasons.

Relationship to current change: Phase 0.2 specifies exact-handle single-slot no-ops
for both models and guards, after policy checks at every ancestor.

Why it matters: Innocent identity writes invalidate borrowed models, run validators
and change iterator/cache lifecycle; the shortcut inconsistently honors freezing.

Why this blocks the current change: The required AC-011 semantics are observably
incorrect through supported public assignment syntax.

Required behavior: Recognize same-slot owned DictModels as well as guards and apply
full liveness/existence/ancestor policy before returning without transaction.
Bulk same-handle update remains an ordinary replacement.

Acceptance criteria: All SOL-003 tests pass with preserved identity, zero root
validation and preserved iterator for allowed no-ops; frozen requests fail with
frozen_instance and unchanged state; augmented/bulk fixtures still pass.

Verification artifact: `tests/test_sol_phase02_blockers.py`, `test_sol003_*`.
Verification status: **CONFIRMED FAILING — 3 cases**.

## SOL-004 — Compatibility isolation and rebuild lifecycle are unfinished

Severity: **High**. Disposition: **BLOCKER**.
Related AC: **AC-017**, **AC-023**, **AC-016**.

Location: `src/pydandict/_compat.py:13`, `:56`;
`src/pydandict/_core.py:70`, `:235`, `:251`, `:517`;
`src/pydandict/_containers.py:14`.

Problem: The adapter mainly wraps unchecked casts. Allocation, raw slot reads and
swaps, schema rewriting and compiled cache ownership remain in core. Required
schema shapes are not checked. Class-local alias/canonical caches have no rebuild
invalidation. Private root/container/transaction protocols remain broadly Any-based,
rather than containing Any at the prescribed adapter/public boundaries.

Evidence: After a failed alias-mode validation compiles a variant before the first
successful instance, force rebuild replaces the schema but returns the identical
old compiled variant. Setting the required schema to None makes adapter access
return None without the compatibility diagnostic. AST verification reports raw
Pydantic slot operations and schema compilation in core. Static inspection finds
Owned._root/_data, transaction callbacks and MutableSequence/Mapping/Set[Any]
throughout private control flow despite strict Pyright reporting no errors.

Relationship to current change: Isolating and qualifying this boundary is an
explicit Phase 0.2 architecture requirement, not a discretionary refactor.

Why it matters: Rebuild can use stale compiled behavior; incompatible structures
fail through unchecked paths; nominal strictness does not verify private contracts.

Why this blocks the current change: AC-017 is directly unsatisfied and AC-023's
required source assurance is incomplete.

Required behavior: Consolidate version-sensitive operations behind the adapter,
assert consumed structures, invalidate all compiled variants for supported rebuilds,
and supply the typed private interfaces required by the approved architecture.
No new exported guard API or dependency expansion is required.

Acceptance criteria: SOL-004 tests pass; canonical and alias variants recompile
after schema replacement, remain class-local and reuse unchanged schemas;
unsupported shapes/version fail with incompatible-pydantic TypeError; all strict
source checks pass without broad Any control flow or suppression.

Verification artifact: `tests/test_sol_phase02_blockers.py`, `test_sol004_*`, plus
manual private typing/boundary audit.
Verification status: **CONFIRMED FAILING — 3 automated cases and static audit**.

## SOL-005 — Typing verifier accepts incomplete or unexpected proof

Severity: **Medium**. Disposition: **BLOCKER**.
Related AC: **AC-023**, **AC-024**.

Location: `tools/check_typing.py:37`, `:66`.

Problem: Positive coverage accepts any two analyzed files. Negative diagnostics
are reduced to a set; duplicate diagnostics disappear and errors without a rule
are skipped. Nonzero status is accepted without requiring the expected error exit
and consistent summary counts.

Evidence: A fabricated successful report with only two files passes despite the
required source/helper/fixture set being larger. The complete expected four errors
plus a duplicate or an unruled syntax error also passes. Three verifier failure
controls fail because the helper does not reject these reports.

Relationship to current change: Phase 0.2 introduces this actual typing gate and
explicitly requires full source coverage and exact negative diagnostics.

Why it matters: Required CI can turn green after source exclusions or additional
typing failures without actually verifying the contract.

Why this blocks the current change: It prevents meaningful enforcement of AC-023
and AC-024 even though today's legitimate Pyright invocation passes.

Required behavior: Verify the intended complete source set/configuration and
analyzed coverage. Compare the complete diagnostic multiset, rejecting missing,
duplicate, unexpected, malformed/unruled errors and inconsistent exit/summary data.

Acceptance criteria: SOL-005 failure controls pass; real positive strict sources
still pass and all four existing negative rule/line errors are exactly verified.

Verification artifact: `tests/test_sol_phase02_blockers.py`, `test_sol005_*`.
Verification status: **CONFIRMED FAILING — 3 controls**.

## SOL-006 — Artifact qualification exercises only one wheel

Severity: **High**. Disposition: **BLOCKER**.
Related AC: **AC-025**, **AC-026**, installed portion of **AC-023**.

Location: `tools/qualify_package.py:46`, `:70`, `:101`, `:121`;
`.github/workflows/check.yml`, qualification job.

Problem: The sdist-rebuilt wheel is hashed but never installed. A single venv with
HTTP/type dependencies is used for direct-wheel consumers; no bare library-only
consumer exists. The import-root assertion is written into a file only analyzed
by Pyright, never executed. Installed negative typing and verifytypes checks and
exact resolved dependency records are absent. The runtime HTTP consumer checks
only a successful GET rather than the required request/422/schema contract.

Evidence: The real helper completed successfully and printed two artifact hashes.
A mocked orchestration contract captures only one installed wheel path. Source
inspection confirms no run of typing_consumer.py, installed negative fixture,
verifytypes command or dependency record. CI runs this helper in both required
Ubuntu versions, so both passing lanes repeat the same missing proof.

Relationship to current change: Production artifact qualification is new in Phase
0.2 and explicitly covers both artifact forms and independent consumers.

Why it matters: A broken rebuilt artifact or dependency/source-path fallback can
ship while the required release gate reports success.

Why this blocks the current change: AC-026 is not satisfied and AC-025 cannot enforce
its required artifact consumers.

Required behavior: For each wheel, run isolated bare-library and HTTP consumers,
runtime site-packages/package-root assertions, installed strict positive/negative
typing and 100% completeness. Record exact resolved dependencies and hashes;
clear source/prototype paths and fail nonzero when required proof is missing.

Acceptance criteria: SOL-006 orchestration check passes, then actual qualification
demonstrates every prescribed consumer for both wheels on Ubuntu 3.11/3.14.
Hashing or merely installing the second wheel is insufficient.

Verification artifact: `tests/test_sol_phase02_blockers.py`, `test_sol006_*`,
actual helper execution and orchestration inspection. The automated test catches
the minimum missing second-artifact invariant; it does not replace full consumers.
Verification status: **CONFIRMED FAILING — 1 contract case; weak helper passes**.

## SOL-007 — Benchmark is not the approved production comparison

Severity: **Medium**. Disposition: **BLOCKER**.
Related AC: **AC-027**.

Location: `tools/benchmark.py:35`, `:57`; `docs/phase-0.2-plan.md`, P02-6.

Problem: The baseline is a plain dict rather than unmodified production `07fec9b`.
Only width 1000 construction plus one edit is measured with three timed samples
and tracemalloc enabled during timing. Deep/mixed workloads, required operations,
warmups/sample counts, p95, separate allocations, validation counters, source
hashes and complete environment metadata are missing. The sole result assertion
checks an unrelated one-element instance rather than each measured operation.

Evidence: Running the benchmark emits one large_values workload, repeats=3,
median_ms/median_peak_bytes and no baseline source commit. SOL-007 fails because
the required source baseline is absent. CI redirects the output to a transient
benchmark.json without a durable evidence record.

Relationship to current change: The approved Phase 0.2 performance contract is
qualification evidence, not a speed target or production optimization request.

Why it matters: The measurements cannot establish production baseline/candidate
behavior or reproduce the agreed large/deep workload assessment.

Why this blocks the current change: It directly violates the required AC-027 report.

Required behavior: Execute unchanged baseline and candidate on one environment
using widths 10/100/1000/10000, linear depths 1/5/20 and the specified mixed graph;
cover reads, scalar/coupled/rejected/nested writes, copy and Python/JSON dump.
Use at least five warmups, 100 timed samples, 10,000 reads, three complete runs per
revision, separate allocation measurement, result assertions and validation counts.
Record median/p95, source commits/hashes and the approved metadata. Timing remains
observational; no speed budget is introduced.

Acceptance criteria: SOL-007 baseline check passes and the complete prescribed
measurement/evidence protocol is demonstrated. Adding a commit string alone does
not satisfy this finding.

Verification artifact: `tests/test_sol_phase02_blockers.py`, `test_sol007_*`,
actual benchmark output and manual protocol comparison.
Verification status: **CONFIRMED FAILING — 1 report contract case**.

## SOL-008 — Contract documentation and AC evidence are unfinished

Severity: **Medium**. Disposition: **BLOCKER**.
Related AC: **AC-028**.

Location: `docs/research/`; `docs/nested-values.md:3`;
`docs/mutation-semantics.md:3`; `docs/decisions/README.md`.

Problem: Required phase-0.2-results.json and phase-0.2-findings.md do not exist.
Target API/ownership/mutation documentation and proposed decision statuses have
not been finalized against verified behavior. README/typing/compatibility updates
do not supply the complete contract/migration/AC trace required by the plan.

Evidence: The evidence-file verification fails at the missing JSON record. The
ownership and mutation documents still call their contract proposed; relevant
decisions remain proposed/target rather than recording demonstrated implementation
outcomes. Deferred/generic/hash/identity behavior disagrees with the target contract.
The Markdown gate passes links/examples but cannot prove contract agreement.

Relationship to current change: P02-6 explicitly requires final evidence and
documentation, preserving historical prototype records.

Why it matters: Users and reviewers cannot distinguish verified production behavior
from proposals or trace every AC to an actual qualifying result.

Why this blocks the current change: AC-028 and the approved definition of done
require these deliverables; their absence is an in-scope omission.

Required behavior: After remediation, finalize affected contracts/decisions,
executable ABC/specialization migration guidance, matrix and diagnostics; create
both required evidence records mapping every AC to real outcomes and preserve
historical records. Do not substitute this blocker report for qualifying evidence.

Acceptance criteria: SOL-008 presence check passes; full documentation/evidence
review agrees with tested behavior and every AC has traceable actual proof.

Verification artifact: `tests/test_sol_phase02_blockers.py`, `test_sol008_*`, plus
manual documentation/decision/AC evidence audit.
Verification status: **CONFIRMED FAILING — 1 minimum artifact case**.

## SOL-009 — Old cache storage survives beyond the guarded commit

Severity: **Medium**. Disposition: **BLOCKER**.
Related AC: **AC-021**.

Location: `src/pydandict/_core.py:280`, `:291`, `:398`, `:868`.

Problem: The recursive preparation function closes over itself and its updates.
The resulting cycle retains installed storage dictionaries after preparation has
returned. After a later storage swap, discarded caches can therefore survive
until cyclic GC, beyond the transaction's busy guard.

Evidence: A cached computed Marker is obtained without retaining it externally;
a two-field update completes, followed by gc.collect(). Its destructor observes
the new values `(2, 3)` but `_pd_busy=False`. Required observation is the complete
new values while busy remains True. Referrer inspection traced the retained old
storage tuple/list to `_prepare.<locals>.prepare` closure cells for updates and
prepare. The focused test fails with `[(2, 3, False)]` versus `[(2, 3, True)]`.

Relationship to current change: Old storage/cache disposal timing is an explicit
Phase 0.2 hardening requirement, even if the underlying preparation pattern was
inherited. The independent swap-fault tests pass; this is a distinct disposal
root cause, not another partial-swap symptom.

Why it matters: Commit-triggered disposal escapes the promised reentry guard and
resource lifetime. Garbage-collector timing can permit callback mutation later.

Why this blocks the current change: AC-021 explicitly requires disposal after all
swaps while the same-root guard remains active. The observable lifecycle violates
that in-scope invariant.

Required behavior: Release preparation/undo references to obsolete storage in the
guarded transaction lifecycle, after all swaps. Callbacks observe the completed
root and same-root mutation/copy remains rejected during disposal. Preserve full
rollback and avoid forcibly collecting unrelated global garbage as a substitute.

Acceptance criteria: SOL-009 observes exactly the complete new values with busy
True; all swap-boundary rollback, reentry and GC/bookkeeping checks still pass.

Verification artifact: `tests/test_sol_phase02_blockers.py`, `test_sol009_*`.
Verification status: **CONFIRMED FAILING — 1 lifecycle case**.

## Quality gates and independent verification

| Executed gate / probe | Result | Classification / limit |
| --- | --- | --- |
| Original pytest suite, before review tests | 93 passed | Existing suite passes. |
| Focused Sol verification | 19 failed, all expected reasons | EXPECTED BLOCKER VERIFICATION. No skips/xfails added. |
| Full pytest suite with review tests | 93 passed, 19 expected failures | Only blocker verification fails. |
| Ruff check: src, tests and three qualification helpers | Pass | Review tests lint clean; production configuration unchanged. |
| Ruff format check: same paths | Pass | Review tests conform. |
| tools/check_typing.py | Pass | Real positive/negative checks pass; SOL-005 exposes verifier weaknesses. |
| pyright --verifytypes pydandict --ignoreexternal | Pass, 100% | Editable source installation; does not substitute for SOL-006 installed wheel checks. |
| tools/check_docs.py | Pass | Links/examples pass; no semantic/evidence completeness guarantee. |
| tools/qualify_package.py | Pass | Build, Twine, sdist rebuild and direct-wheel HTTP/positive typing work; SOL-006 missing consumers remain. |
| tools/benchmark.py | Pass exit, report emitted | SOL-007 report fails the approved contract. |
| Nested transaction, every before/after swap boundary | 60 successful rollback checks over 30 swaps | KeyboardInterrupt: values, fields-set and four handles preserved, busy/ContextVars reset, later write succeeds. |
| Weakrefs / 500 replacements | Pass | Discarded handles collected; bookkeeping bounded by reachable nodes. |
| Supported annotations, update counters, construction contexts, iterator and cache probes | Pass | Independent passing probes described in AC table. |
| Cached-computed disposal / closure referrer probe | Expected failure confirmed | SOL-009, not a successful lifecycle qualification. |

The latest existing [candidate CI run](https://github.com/eddiethedean/pydandict/actions/runs/34802350758)
was inspected: all eight compatibility lanes, two qualification lanes and docs
passed at `1123702`. Release-only preflight was correctly skipped on normal CI.
Release dependency inspection confirms `check -> build -> publish`; publication
was not triggered during review. The remote matrix has not been rerun with the
new failing review tests. Local checks do not claim independent execution of
every remote runtime or the missing full artifact/benchmark protocols.

There are no observed non-review required gate failures to label CHANGE-CAUSED.
The intentional failures are EXPECTED BLOCKER VERIFICATION. Passing weak helpers
are not acceptance evidence for the portions identified above.

## Follow-ups and observations

No new unrelated follow-ups or observations were identified. Open GitHub issues
were searched. Existing [issue #1](https://github.com/eddiethedean/pydandict/issues/1)
already tracks the plan's explicitly excluded security-policy/private-reporting
work; it does not block Phase 0.2 and no duplicate issue was created.

## Convergence and handoff

- Previous blockers resolved: 0; no prior review findings.
- Blockers remaining: 9, SOL-001 through SOL-009.
- New blockers attributable to remediation: 0; no remediation has occurred.
- New unrelated follow-ups discovered: 0.
- Convergence: initial review establishes a bounded contract; not yet a remediation loop.

Only SOL-001 through SOL-009 go to implementation. Preserve these IDs on re-review,
run their existing verification first, inspect fixes/root causes and check
remediation regressions. Minimum automated checks do not replace the complete
required behaviors stated in each finding. Production implementation is unchanged;
verification artifacts remain on the current branch and were not pushed.

**NEEDS FIXES**
