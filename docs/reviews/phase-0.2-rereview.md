# Sol — Phase 0.2 production re-review

Verdict: **NEEDS FIXES**.

Reviewed source: the dirty working tree based on
`1123702ed080e09e00e9dee1392dcebff62e41a9`. The package and benchmark harness
hashes match the implementation evidence. The authoritative scope remains
[the approved Phase 0.2 plan](../phase-0.2-plan.md), including its explicit non-scope,
AC-001–028 and verification matrix. The original implementation boundary is
`83ce43f`/`1123702`; this re-review examines the subsequent remediation diff.

Read the [original review](phase-0.2-review.md),
[resolution report](../research/phase-0.2-remediation.md),
[implementation evidence](../research/phase-0.2-results.json), affected production
code, tests, docs, configuration and workflows. The current package metadata
remains 0.1.0 and Phase 0.2 is unreleased. Persistence, thread/async safety, broader
dependencies, external trials and unrelated policy/prototype cleanup remain excluded.

The pre-existing 133-case suite, including all 19 original Sol cases, passed.
Those minimum reproductions do not fully constrain the original findings:
three annotation-resolution/completion paths and two key-insertion paths still fail the contract.
The typing refactor also introduced an input-callback guard regression.
Public revalidation of an existing model also loses supplied context. This behavior
is present on the approved baseline, but AC-009 explicitly requires it to follow
the pinned Pydantic control; it is therefore an in-scope blocker.

This review changes only verification artifacts: this report, its
[results record](phase-0.2-rereview-results.json), and
[eight protected verification cases](../../tests/test_sol_phase02_rereview.py).
Production implementation, workflows, original Sol tests/report and historical
evidence were not modified. No branch changes were committed or pushed by this review.

## Acceptance criteria

Statuses apply to the reviewed change, not repository-wide perfection. Passing
local checks do not assert execution of the unrun current remote matrix.

| AC | Status | Verification / remaining gap |
| --- | --- | --- |
| AC-001 | VERIFIED | ABC/type assertions, safe scalar/aggregate, specialized generic and finite recursive fixtures pass; actual benchmark shapes construct on both revisions. |
| AC-002 | NOT SATISFIED | SOL-001: named concrete type aliases and parent completion of deferred nested concrete fields/typed extras escape. Direct/deferred-rebuild and generic rejection controls pass. |
| AC-003 | PARTIALLY SATISFIED | SOL-002: cloning rejects model keys/members and direct ingress controls pass; setdefault/pair-update bypass the required unsafe-key check before native hashing. Other cycle/value/timezone controls pass. |
| AC-004 | VERIFIED | Required config/default/revalidation/hook/namespace/extra-policy checks preserved; affected fixtures pass. Typed-extra annotation completion is AC-002. |
| AC-005 | VERIFIED | Nominal model/mapping identity, canonical ordering, shared state, equality and frozen behavior preserved by API/static fixtures. |
| AC-006 | REGRESSED | Coupled model updates and ordinary inventory pass, but SOL-010 allows a same-root input callback to commit before a nested mapping update fails. |
| AC-007 | REGRESSED | Ancestor constraints and frozen identity fixes pass; SOL-010's failed input leaves marker/fields-set changed and guard iterators invalidated. |
| AC-008 | VERIFIED | Drift/topology rejection, shape-changing output and independent stateful controls remain green. |
| AC-009 | NOT SATISFIED | SOL-012: public model_validate(existing_model, context=...) discards supplied context. Raw Python/JSON/strings, alias and caller-namespace controls pass; canonical mutation/copy context remains None. |
| AC-010 | VERIFIED | Adoption/repetition isolation, retained/reordered identity, union replacement and stale-handle fixtures pass. |
| AC-011 | VERIFIED | All SOL-003 cases pass: nested model identity no-ops, zero validation, preserved iterators and ancestor freezing; augmented-assignment controls remain green. |
| AC-012 | REGRESSED | Ordinary creation/exhaustion/local-version behavior preserved, but a SOL-010 input failure invalidates an existing guard iterator after an unexpected callback commit. |
| AC-013 | VERIFIED | Detached usable removals and result-preparation rollback fixtures pass; installation path inspected. |
| AC-014 | VERIFIED | Supported copy/deepcopy/guard-detachment and trusted-path controls pass; hash-position clone defect no longer exposes blank models. |
| AC-015 | VERIFIED | Explicit metadata, reset/default factory and computed-cache fixtures pass; storage preparation preserves metadata/cache failure behavior. |
| AC-016 | PARTIALLY SATISFIED | Stable policy/programming-error controls pass; SOL-002 still returns native unhashable TypeError instead of the specified unsupported-value prefix. |
| AC-017 | VERIFIED | Checked adapter owns raw allocation/storage/schema/serializer/cache operations; original AST/shape/rebuild tests and new adapter tests pass. Manual version rejection and canonical/alias reuse/invalidation verified. |
| AC-018 | VERIFIED | Supported Pydantic serializer, exclusion, alias, computed/context, schema and framework-output fixtures pass, including JSON Schema example metadata. |
| AC-019 | VERIFIED | Source TypeAdapter/BaseModel-envelope/FastAPI integration passes; both rebuilt/direct artifact consumers execute real 200/422/OpenAPI checks. |
| AC-020 | REGRESSED | SOL-010: list-slice and mapping-update input callbacks run before the same-root guard. Other reentry and BaseException recovery controls pass. |
| AC-021 | VERIFIED | Protected cache finalizer observes complete `(2, 3)` while busy; enumerated 82 before/after injections over 41 prepared swaps pass with recovery. |
| AC-022 | VERIFIED | Live-handle root retention/collection and 500-replacement weakref/current-node checks pass with the typed coordinator. |
| AC-023 | VERIFIED | Real strict run covers eight intended files with zero errors; private payload/root/transaction contracts now typed; local and both isolated installed verifytypes reach 100%. |
| AC-024 | VERIFIED | Real independent four-error fixture and original incomplete/duplicate/unruled failure controls pass; exact multiset, exit/count, configuration and fixture location enforced. |
| AC-025 | PARTIALLY SATISFIED | Eight mandatory lanes, docs/artifact gates and release dependency chain exist, but no successful workflow verifies the current dirty-tree candidate. SOL-006 remains open for actual matrix proof. |
| AC-026 | PARTIALLY SATISFIED | Fresh local qualification exercises both wheels in four clean environments with import-root, HTTP, typing/completeness, marker and dependency/hash proof. Required Ubuntu 3.11/3.14 executions remain absent. |
| AC-027 | VERIFIED | Actual protected benchmark execution completes; durable same-source evidence contains real production baseline, eight shapes/50 applicable cells, three runs per revision, required samples, correctness/counts, separate allocation, latency/p95 and environment/source/harness hashes. |
| AC-028 | PARTIALLY SATISFIED | Evidence/migrations/decisions now exist and preserve history, but completion claims need final reconciliation with SOL-001/002/010/012 and current matrix outcomes under SOL-008. |

## Previous blockers

| Finding | Status | Verification / actual fix |
| --- | --- | --- |
| SOL-001 | PARTIALLY FIXED | Original three cases and four added extra-annotation controls pass. A named-alias and two parent-completion cases fail; audit still misses resolved alias/nested schema annotations. |
| SOL-002 | PARTIALLY FIXED | Original three hash-position cases and three direct-ingress cases pass. Two new model-key insertion cases fail the required diagnostic. |
| SOL-003 | VERIFIED FIXED | Original three identity/frozen-ancestor cases pass; implementation recognizes both guard/model identities and checks ancestors. |
| SOL-004 | VERIFIED FIXED | Original three controls, ten adapter cases, source typing and manual compile/version probes pass. Raw/schema/cache boundary and private generic contracts inspected. |
| SOL-005 | VERIFIED FIXED | Original three failure controls and actual eight-file/four-error gate pass; diagnostic multiplicity and source/fixture coverage are enforced. |
| SOL-006 | PARTIALLY FIXED | Original orchestration control and fresh full local consumers pass for both wheels. Required candidate Ubuntu 3.11/3.14 and full CI proof remains unavailable. |
| SOL-007 | VERIFIED FIXED | Original report control executes the complete actual comparison successfully. Source extraction, fixture/operation protocol and matching durable report inspected. |
| SOL-008 | PARTIALLY FIXED | Original artifact-presence case and Markdown gate pass. Final contract/AC evidence is not complete while code blockers and current matrix proof remain open. |
| SOL-009 | VERIFIED FIXED | Original disposal case passes; recursive closure is released on success/failure. All prepared slot positions, cleanup, handle preservation and later recovery verified. |

The remaining SOL-001 and SOL-002 findings retain their IDs: their new cases
demonstrate unresolved parts of the same required invariants, not new scope.

## SOL-001 — Completed annotation envelope is not enforced

Severity: **High**. Disposition: **BLOCKER**. Related AC: **AC-002**.

Location: `src/pydandict/_core.py:266–321`, `:552–563`, `_check_annotation`;
`src/pydandict/_compat.py:334–335`.

Problem: The audit does not resolve named TypeAliasType values and remains
conditional on not being in `_BUILDING` for nested validation. A parent can
compile a child schema whose previously unresolved field/extra annotation resolves
to a concrete mutable type. The parent audit only recognizes the child class;
the nested validation skips the audit. Child class metadata can still report
incomplete even though the parent has a usable compiled child schema.

Evidence: Define Child with `numbers: "Later"`, then `Later = list[int]`, then
Parent with `child: Child`. `Parent(child={"numbers": [1]})` succeeds and returns
an OwnedList, while Child remains incomplete. The analogous deferred
`__pydantic_extra__: dict[str, "Later"]` also succeeds. A field annotated with
`TypeAliasType("Concrete", list[int])` likewise constructs with an OwnedList.
All three new tests report `DID NOT RAISE TypeError`; explicit child rebuild is
unnecessary for the nested bypass. The alias test also protects the supported
MutableSequence alias alternative from blanket rejection.

Relationship to current change: This is the original completed-schema invariant
from SOL-001, partially addressed for direct/rebuild paths. No annotation type or
runtime API is being added to scope.

Why it matters: Normal nested construction still permits a declared concrete
mutable API whose returned object has a different runtime identity.

Why this blocks the current change: AC-002 explicitly forbids escape through
deferred completion and nested construction; passing only the original direct
completion reproducer is insufficient.

Required behavior: Resolve named aliases and audit the annotations actually resolved
for all nested schemas before unsupported instances escape, including typed-extra value metadata. Preserve
legitimate deferred declarations, finite recursion and supported specialization.

Acceptance criteria: All three new SOL-001 cases and all original cases pass with the
unsupported-annotation TypeError/ABC hint, whether detection occurs at parent
schema setup or construction. Existing recursive/generic/ABC fixtures remain green.

Verification artifact: `tests/test_sol_phase02_rereview.py`, `test_sol001_*`.
Verification status: **CONFIRMED FAILING — three missing rejections**.

**ESCALATION RECOMMENDED:** the direct-path fix plus remediation continuation
still miss resolved-annotation/completion boundaries. Use stronger implementation reasoning
and reconsider the bounded alias resolution/audit placement across nested compiled schemas; do
not apply another input-specific check or redesign unrelated ownership machinery.

## SOL-002 — Unsafe hash-position ingress remains incomplete

Severity: **Medium**. Disposition: **BLOCKER**.
Related AC: **AC-003**, **AC-016**.

Location: `src/pydandict/_containers.py:322`, `:331–333`.

Problem: Model-key safety is checked for direct assignment but not before
setdefault membership/insertion or materializing pair-update input as a dict.
Those paths perform native hashing before the closed-value policy checks the key.

Evidence: On `MutableMapping[Any, int]`, `table.setdefault(Key(number=1), 2)` and
`table.update([(Key(number=1), 2)])` raise `TypeError: unhashable type: 'Key'`.
The expected `pydandict_unsupported_value:` prefix is absent. Both new tests fail
the prefix assertion. State remains unchanged in these reproductions; the earlier
accepted/hash-position clone corruption is fixed, hence lower remaining severity.

Relationship to current change: This is the original unsafe-key boundary and
diagnostic contract. The pair input is otherwise well formed; it is not an
unrelated malformed-pair requirement or a request to support model keys.

Why it matters: Equivalent unsupported keys receive different public diagnostics,
and not every insertion path checks hash safety before native hashing.

Why this blocks the current change: The approved stable diagnostic for unsafe
actual keys is an explicit in-scope guarantee under AC-016 and SOL-002.

Required behavior: Reject model/guard/unsafe aggregate insertion keys using the
closed-value diagnostic before native hash operations, across supported insertion
paths. Preserve ordinary safe keys, update precedence, no-op semantics and recovery.

Acceptance criteria: Both new cases and all original/direct-ingress controls pass;
saved values, fields-set, handles and iterators remain unchanged on rejection, and
subsequent valid insertion succeeds.

Verification artifact: `tests/test_sol_phase02_rereview.py`, `test_sol002_*`.
Verification status: **CONFIRMED FAILING — two incorrect diagnostics**.

**ESCALATION RECOMMENDED:** the cloning fix and direct-ingress continuation did
not cover all insertion boundaries. A stronger implementation audit of the shared
key-safety invariant is warranted; no new public collection API is needed.

## SOL-006 — Artifact/matrix qualification is not complete

Severity: **Medium**. Disposition: **BLOCKER**.
Related AC: **AC-025**, **AC-026**.

Location: `.github/workflows/check.yml`, qualification/compatibility jobs;
`docs/research/phase-0.2-results.json`, `ci.current_candidate_run`.

Problem: The substantive helper omissions are fixed, but the required actual
candidate matrix has not run. Local macOS/Python 3.11 proof does not qualify the
mandated Ubuntu 3.11/3.14 artifact consumers or eight runtime lanes.

Evidence: Fresh helper execution passes both artifact forms in four clean venvs,
including actual library/HTTP/typing runs, exact negative errors and completeness.
GitHub's latest CI is still run 34802350758 at unmodified committed `1123702`;
the current evidence explicitly sets current_candidate_run to null. No current
remote execution result was found or fabricated.

Relationship to current change: The original SOL-006 acceptance contract explicitly
requires those Ubuntu executions, and AC-025 requires successful candidate CI.

Why it matters: Current version-sensitive/runtime changes remain unverified on
the finite matrix the package intends to qualify.

Why this blocks the current change: Required in-scope verification is absent,
not a request for broader platforms or repository-wide quality improvements.

Required behavior: After code remediation, execute the complete current candidate
workflow and both Ubuntu artifact lanes; retain source/run identity, actual outcomes
and exact per-environment records. Do not alter or skip failing required lanes.

Acceptance criteria: The identified candidate's eight runtime lanes, docs/typing/
lint/format and Ubuntu 3.11/3.14 artifact qualification all succeed, with traceable
run URLs and artifact/dependency evidence.

Verification artifact: Existing `test_sol006_*` plus actual GitHub workflow and
helper executions. Verification status: **LOCAL IMPLEMENTATION VERIFIED;
CURRENT REMOTE PROOF NOT RUN — ENVIRONMENTAL/UNAVAILABLE**.

No further production-helper defect was established in this re-review. This item
needs candidate execution/evidence, not speculative packaging refactoring.

## SOL-008 — Final contract evidence is not reconciled

Severity: **Medium**. Disposition: **BLOCKER**. Related AC: **AC-028**.

Location: `docs/research/phase-0.2-results.json`, AC trace;
`docs/research/phase-0.2-findings.md`; `docs/decisions/README.md`, D23/D26/D28.

Problem: The missing deliverables are supplied, but their implementation-completion
claims are not yet supported across the approved contract: the new SOL-001/002/010/012
verification fails and current matrix execution remains missing. The recorded
133 passing tests are genuine historical self-verification, not fabricated; they
cannot establish the uncovered behavior or substitute for current remote proof.

Evidence: The record labels every AC IMPLEMENTED/local PASS; the findings say the
completed annotations, immutable hash positions and contract agreement are final.
D23/D26/D28 are implemented, while the corresponding completion/failure/matrix
obligations remain unsatisfied in this review. Original evidence-presence verification
passes but was explicitly only a minimum artifact check.

Relationship to current change: This is the original final-evidence/agreement
requirement; no historical prototype rewrite or broader documentation cleanup is
required. The production fixes remain owned by their own SOL IDs.

Why it matters: Final evidence must distinguish demonstrated outcomes from
remaining qualification and agree with the implementation users will receive.

Why this blocks the current change: AC-028 requires truthful final AC trace and
contract agreement, not merely the two required filenames.

Required behavior: After the production blockers and matrix verification, refresh
the final evidence/source hashes/test counts/current CI URLs and corresponding
decision/contract claims. Preserve the original review and prototype records as
history. Do not satisfy this item by relabeling incomplete outcomes as verified.

Acceptance criteria: Every AC is traceable to an actual qualifying result, the
remaining verification passes, current source and artifact identities are recorded,
and final documentation accurately separates released 0.1.0 from this candidate.

Verification artifact: Original `test_sol008_*`, documentation gate, source/report
consistency audit and actual AC/matrix results. Verification status: **ARTIFACT
PRESENCE/LINKS VERIFIED; FINAL CONTRACT AGREEMENT PARTIAL**.

## SOL-010 — Input materialization escapes the same-root guard

Severity: **High**. Disposition: **BLOCKER**.
Related AC: **AC-006**, **AC-007**, **AC-012**, **AC-020**.

Location: `src/pydandict/_containers.py:163`, `:322–324`.

Problem: The private typing refactor moved list-slice and dict-update iterable
materialization out of the `_change` callback. Input code runs before liveness and
the root transaction/busy guard are acquired.

Evidence: An iterable sets `model.marker = 9`, yields a valid element/pair, then
raises ValueError. Slice assignment and nested mapping update both propagate the
late failure with marker already committed as 9. An existing guard iterator is
invalidated. The same source extracted at `1123702` rejects the callback write with
`pydandict_reentrant_transaction:` and leaves marker 0 for both operations.
Both new regression tests fail with the unexpected late ValueError.

Relationship to current change: **INTRODUCED BY REMEDIATION**, established by
actual unmodified-source execution and the diff: those materializations previously
occurred inside the guarded callback. This is a new root cause, separate from the
fixed SOL-009 cache-disposal closure.

Why it matters: A failed ordinary container mutation changes live values,
fields-set and iterator generations before its own transaction begins.

Why this blocks the current change: It is a substantive atomicity/reentry regression
in the exact behavior being hardened; the plan explicitly requires guard acquisition
before consuming operation iterables or invoking callbacks.

Required behavior: Run operation input callbacks under the same-root guard before
live mutation, preserve committed reads, reject same-root mutation/copy reentry and
release guards after failure. Stale/frozen/error-policy handling must remain sound.

Acceptance criteria: Both new cases reject with the reentry RuntimeError, preserve
values, fields-set, saved handles and iterators, and allow subsequent valid writes.
Ordinary valid slice/mapping updates and original callback/recovery tests still pass.

Verification artifact: `tests/test_sol_phase02_rereview.py`, `test_sol010_*`.
Verification status: **CONFIRMED FAILING — two state-changing input failures**.

## SOL-012 — Existing-model public validation drops supplied context

Severity: **Medium**. Disposition: **BLOCKER**. Related AC: **AC-009**.

Location: `src/pydandict/_core.py:329–333`, `:564–565`, `:597–613`.

Problem: The public entry forwards context to the entry validator, but its schema
wrapper sends existing DictModel inputs through the context-free canonical
validator. That validator is intended for mutations/copies, not for dropping the
context supplied to a public construction/validation call.

Evidence: With matched after-validators recording `ValidationInfo.context`, raw
dictionary validation delivers `{"request": 2}` in both classes. For an existing
instance, BaseModel with `revalidate_instances="always"` observes that dictionary;
DictModel observes `None`. The protected test fails the differential assertion.
Actual isolated execution of unmodified `07fec9b` reproduces the same mismatch.

Relationship to current change: **PRE-EXISTING BUT EXPLICITLY IN SCOPE**. AC-009
requires public construction/validation context to follow pinned control behavior,
including the supported existing-model input. This is not a requirement to retain
request context for subsequent mutation/copy, which must continue using None.

Why it matters: A supported public validation call silently changes what a
context-aware validator sees; the same logical value validates differently based
on whether input is a dictionary or an existing model.

Why this blocks the current change: It violates the explicit AC-009 compatibility
contract. The baseline reproduction establishes provenance, not an exemption from
an approved in-scope acceptance criterion.

Required behavior: Preserve supplied public context for existing-model validation
according to the pinned control, without retaining it for later canonical
transactions/copies or weakening input isolation/revalidation.

Acceptance criteria: The matched raw-input and existing-model context controls
pass; the resulting model remains usable, and subsequent mutation and model_copy
validate with context=None. Existing mode/alias/context and ownership tests pass.

Verification artifact: `tests/test_sol_phase02_rereview.py`,
`test_sol012_existing_model_public_validation_preserves_supplied_context`.
Verification status: **CONFIRMED FAILING — supplied context becomes None**.

## Follow-ups

| Finding | Severity | GitHub status |
| --- | --- | --- |
| SOL-011 — Repeated recursive-root after-validator invocation | Low | CREATED ISSUE #2 |
| Existing excluded security/private-reporting policy | Previously tracked | EXISTING ISSUE #1 |

### SOL-011 — Repeated recursive-root after-validator invocation

Severity: **Low**. Disposition: **FOLLOW-UP**. Related AC: **NONE**.

Location: `src/pydandict/_core.py`, recursive schema/validation layering;
`tools/benchmark.py`, Chain/RootChain.

Problem: A self-recursive root can invoke its root after-validator twice during
one append or model_copy. A distinct root subclass separates those invocations.

Evidence: Executed the standalone recursive-model reproducer on unmodified
`07fec9b` and the current candidate: both produced two calls for append and copy
and the expected final state. Full reproducer, expected investigation and proposed
verification are in [issue #2](https://github.com/eddiethedean/pydandict/issues/2).

Relationship to current change: Pre-existing on the approved baseline; no duplicate
transaction or changed value was demonstrated. The approved contract explicitly
does not promise that one root pass invokes every nested validator exactly once,
and supported validators are rerunnable/idempotent. No speed budget is in scope.

Why it matters: Extra work and surprising callback counts deserve investigation,
but do not prevent this change from satisfying its bounded contract once blockers
are fixed. No follow-up verification was added to the required suite.

GitHub status: **CREATED ISSUE #2**. Open issues were searched first; only the
unrelated existing [policy issue #1](https://github.com/eddiethedean/pydandict/issues/1)
was found. No semantic duplicate existed.

## Quality gates and verification

| Gate / execution | Result | Classification / limits |
| --- | --- | --- |
| Full suite before new re-review cases: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests -q` | 133 passed in 97.54s | Includes all 19 original Sol cases and the actual full benchmark run. |
| Interim runtime/control repeat: same command with `-k 'not sol007'` | 132 passed, 6 failed, 1 deselected | EXPECTED BLOCKER VERIFICATION. Only the already-executed slow benchmark is omitted from this repeat; no discovery/config exclusion was changed. |
| Interim full-suite repeats before the verification set was final | 133 passed / 6 failed in 102.29s; 133 passed / 7 failed in 102.13s | EXPECTED BLOCKER VERIFICATION; actual full benchmark executed in both. |
| Final complete suite: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests -q` | 133 passed, 8 failed in 110.53s | All 141 cases ran, including all original Sol cases and the actual full benchmark. Only the eight new blocker cases fail, for the expected reasons. |
| Final focused `tests/test_sol_phase02_rereview.py` | 8 failed in 0.19s | EXPECTED BLOCKER VERIFICATION: three SOL-001, two SOL-002, two SOL-010 and one SOL-012 failures confirmed for the stated reasons. |
| Real `python tools/check_typing.py` | Pass | Eight positive files, zero errors and exactly four independent negative errors. |
| `pyright --verifytypes pydandict --ignoreexternal` | Pass, 100% | Local source installation; both artifact installations checked independently too. |
| Ruff check/format on CI paths | Pass | 20 files formatted including the new verification; no production lint/type gate weakened. |
| `python tools/check_docs.py` | Pass | Links/example syntax, not semantic AC completion; final counts in review results. |
| Fresh `python tools/qualify_package.py` | Pass | Build/Twine, direct/rebuilt wheel consumers in four clean environments; runtime site-packages roots, 200/422/OpenAPI, executed positive/negative/completeness and resolved dependencies. Local macOS/Python 3.11 only. |
| Benchmark execution and durable report/hash/protocol audit | Pass | Full protected benchmark execution plus matching measured source/harness; 50 applicable cells in each of three runs per revision, separate latency/allocation/assertions/counts. Timing observational. |
| Adapter compile/rebuild/version probes | Pass | Unchanged-schema cache reuse, both cache invalidations and incompatible-version prefix verified. |
| Unmodified-source callback differential | Regression confirmed | CHANGE-CAUSED: old source rejects reentry with marker 0; remediation permits marker 9 before input failure. |
| Matched public-context control / baseline execution | Contract failure confirmed | SOL-012: BaseModel preserves supplied context; DictModel drops it on both candidate and unmodified baseline. Pre-existing but in-scope AC failure. |
| 82 swap failures / 500 replacements | Pass | Implementation-side executable cases ran in both suite executions. |
| `git diff --check` / protected/source hash comparisons | Pass | Review leaves production and original Sol artifacts unchanged. |
| Current remote eight-lane / Ubuntu artifact matrix | Not run | ENVIRONMENTAL/UNAVAILABLE for the dirty candidate, SOL-006. Latest GitHub success is historical `1123702`, not the remediation tree. |

There are no observed failing pre-existing runtime or required lint/type/package
gates apart from the intentional blocker verification. The implementation report's
repository-wide exploratory lint findings affect unchanged historical/probe paths
outside required CI; this review did not expand lint scope or fix that debt.
The regression underlying SOL-010 is change-caused even though its executable
demonstration is classified EXPECTED BLOCKER VERIFICATION.

## Observations

No additional non-blocking suggestions are handed to implementation. Measured
latency remains observational under AC-027; this review introduces no performance
ceiling or optimization requirement.

## Convergence and bounded handoff

- Previous blockers resolved: **5** — SOL-003/004/005/007/009.
- Previous blockers remaining: **4** — SOL-001/002/006/008, partially fixed.
- New blockers attributable to remediation: **1** — SOL-010.
- Newly identified in-scope baseline blocker: **1** — SOL-012.
- Total blockers remaining: **6**; four need production remediation, one needs
  actual candidate matrix verification, and one needs final evidence reconciliation.
- Follow-ups captured: **1** new issue, SOL-011/#2; existing excluded #1 retained.
- Convergence: substantial improvement, but not yet converged. Existing annotation/
  hash invariants need complete boundary fixes, and input materialization needs its
  guarded lifecycle restored. Public existing-model validation must preserve its
  supplied context. Escalation is recommended for the repeated partial
  SOL-001/002 fixes, not for a repository-wide redesign.

Only **SOL-001, SOL-002, SOL-006, SOL-008, SOL-010 and SOL-012** remain in the blocker handoff.
Do not fix SOL-011/#2, the security-policy follow-up, historical lint debt or other
observations in Luna remediation. Preserve all protected verification and the
stable original IDs. Refresh final evidence after real successful verification;
do not infer PASS from the original 19-case suite alone.

**NEEDS FIXES**
