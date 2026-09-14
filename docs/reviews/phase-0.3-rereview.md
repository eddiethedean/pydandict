# Phase 0.3 — Independent production re-review

Reviewed 2026-09-14 against the [approved contract](../phase-0.3-plan.md),
[initial review](phase-0.3-review.md) and
[remediation handoff](phase-0.3-remediation.md).
Candidate: `532e0401f9e89553f010668200d8984edc37f003` on `main`.
The worktree was clean at entry. Only this report and
[blocker verification](../../tests/test_sol_phase03_rereview.py) were added.
No production code, protected prior tests, dependency, workflow or qualification
record was changed. No commit, push, release or approval was performed.

**One blocker is closed; three remain partially fixed.** The seven original
blocker cases now pass, as does the complete 163-test candidate suite. However,
the SOL-017 replay fixes its two acceptance examples by losing other public-entry
options and moving user validation ahead of input detachment. Qualification
evidence also remains incomplete and can be corrupted by successful mocked tests.
Green CI is genuine, but its existing checks do not establish these invariants.

## Acceptance criteria

IDs mean Phase 0.3 criteria, not historical Phase 0.2 criteria. Retained VERIFIED
criteria use the initial review's contract inspection, re-inspection of affected
code, the independently rerun complete suite and exact-candidate CI. They do not
claim a newly executed exhaustive scalar leaf/mode matrix.

| AC | Status | Evidence / remaining requirement |
| --- | --- | --- |
| AC-001 | PARTIALLY SATISFIED | Original strict strings integer and JSON date controls pass; SOL-017 now accepts a strict JSON string-to-int coercion rejected by pinned BaseModel. |
| AC-002 | VERIFIED | Retained closed-envelope, annotation, unsafe-output and hash-ingress controls pass; installation still audits outputs. |
| AC-003 | VERIFIED | Prototype/inventory and scalar reads retain ABC identity, canonical/default/excluded namespace and ordered extras; installed example uses mapping readers/writers. |
| AC-004 | VERIFIED | Retained read, membership, views, dict/pattern and serializer-separation controls pass; example executes without private APIs. |
| AC-005 | VERIFIED | Retained iterator tests pass; no iterator implementation changed by remediation. |
| AC-006 | VERIFIED | Namespace, protected-name and explicit alias-mode controls pass; mode schema rewriting preserves the tested alias cases. |
| AC-007 | VERIFIED | Bounds, scalar contract and transaction recovery tests pass; scalar oracle checks rejected single writes. |
| AC-008 | VERIFIED | Coupled batch/union and duplicate-precedence controls pass; scalar machine compares atomic batch outcomes to its own oracle. |
| AC-009 | VERIFIED | SOL-014 update/reset cases pass; both staged collections receive complete string checks before per-name policy; prior pop/staging distinctions retained. |
| AC-010 | VERIFIED | Existing-key/no-op and typed/unknown-extra setdefault controls retained and pass. |
| AC-011 | VERIFIED | Destructive inventory and scalar extra-pop oracle pass; declared field and clear protections unchanged. |
| AC-012 | VERIFIED | Reset factory/deduplication/failure controls pass; scalar machine resets values and explicit metadata independently. |
| AC-013 | VERIFIED | Frozen mutation/missing/no-op controls pass; SOL-014 changes only structural-error precedence, not freeze policy. |
| AC-014 | VERIFIED | Snapshot/fields-set controls and new scalar values/order/metadata oracle pass; source example tests reset/removal and copy independence. |
| AC-015 | VERIFIED | Canonical drift/programming-exception and mutation/copy context controls pass; canonical Python transaction validation remains unchanged. |
| AC-016 | VERIFIED | Complete staging reentry, prepared swap and BaseException recovery controls pass; transaction engine not replaced. Public entry source isolation is separately REGRESSED under AC-020. |
| AC-017 | VERIFIED | Computed-cache success/failure/no-op controls pass; cache/commit implementation unchanged. |
| AC-018 | VERIFIED | Parametrized copy ownership and scalar copy controls pass; actual example checks a copy edit leaves its source unchanged. |
| AC-019 | VERIFIED | Trusted-path rejection and inherited API controls pass; no construct/pickle/copy restriction removed. |
| AC-020 | REGRESSED | SOL-017: JSON strict/extra/context options are lost, and a rejected strings callback mutates caller data. The same probes pass before remediation. |
| AC-021 | VERIFIED | Serializer, alias, exclusion, schema and context controls pass; serialization path unchanged. |
| AC-022 | VERIFIED | Retained equality/hash controls pass; equality and hashing unchanged. |
| AC-023 | VERIFIED | Required strict positive/negative helper passes in the original workspace; source completeness is 100%; both advertised installed artifact CI gates pass. |
| AC-024 | PARTIALLY SATISFIED | Fresh reviewer qualification runs actual mapping-only scalar example in both bare wheel paths; SOL-016's explicit installed name/version/license/runtime-requirement policy assertions remain absent. |
| AC-025 | PARTIALLY SATISFIED | Exact candidate's advertised CI lanes succeed and package records exist; SOL-015: durable evidence can be overwritten with missing identity, and complete AC-to-test/lane/settings/limitations reconciliation is absent. |
| AC-026 | VERIFIED | ScalarTransactions retains its own values/order/fields-set oracle, checks rejected outcomes, and runs max_examples=100/stateful_step_count=100/deadline=None/derandomize=True in the passing full suite; nested machine retained. Persisted run/replay evidence remains part of SOL-015. |
| AC-027 | VERIFIED | All 163 candidate tests pass, including prior nested ownership/transaction/stateful controls; no supported nested implementation was removed to narrow the scalar boundary. |
| AC-028 | PARTIALLY SATISFIED | Source/installed examples and docs checker pass; fresh qualification and exact candidate CI succeed. SOL-015 evidence reconciliation and SOL-016 metadata verification remain incomplete. |

## Previous blockers

| Finding | Status | Verification / root-cause inspection |
| --- | --- | --- |
| SOL-014 | VERIFIED FIXED | Both protected cases pass; bulk type guards precede policy and preserve rollback/recovery. |
| SOL-015 | PARTIALLY FIXED | Both original presence cases pass and scalar oracle is real; new evidence-preservation contract fails and complete qualification inventory remains missing. |
| SOL-016 | PARTIALLY FIXED | Protected orchestration and fresh real example execution in both wheels pass. Explicit installed metadata/dependency policy checks still missing. |
| SOL-017 | PARTIALLY FIXED | Original two mode controls pass; four new option/isolation cases fail. These are confirmed remediation regressions within the same unresolved entry-mode root cause. |
| SOL-001 | VERIFIED FIXED | Retained annotation/generic/deferred completion controls pass. |
| SOL-002 | VERIFIED FIXED | Retained hash-ingress controls pass. |
| SOL-003 | VERIFIED FIXED | Retained owned-identity/ancestor freeze controls pass. |
| SOL-004 | VERIFIED FIXED | Retained adapter shape/rebuild controls pass. |
| SOL-005 | VERIFIED FIXED | Strict source inventory and exact negative diagnostics pass. |
| SOL-006 | VERIFIED FIXED | Both artifact CI lanes succeed; direct/rebuilt orchestration retained. |
| SOL-007 | VERIFIED FIXED | Retained benchmark baseline/generator contracts pass. |
| SOL-008 | VERIFIED FIXED | Historical provenance contracts pass; SOL-015 is the distinct current-phase qualification deliverable. |
| SOL-009 | VERIFIED FIXED | Retained finalizer/disposal and swap recovery controls pass. |
| SOL-010 | VERIFIED FIXED | Retained guarded staging/callback reentry controls pass. |
| SOL-012 | VERIFIED FIXED | Protected existing-model Python context differential passes; new JSON/strings context loss is tracked under SOL-017. |
| SOL-013 | VERIFIED FIXED | Protected existing-model Python source ownership controls pass; new strings mapping-input mutation is tracked under SOL-017. |

## Unresolved blockers

### SOL-017 — Mode replay loses entry options and runs callbacks before detachment

Severity: **High**. Disposition: **BLOCKER**. Related AC: **AC-001/020**.

Location: `_compat.py` `wrap_model_schema`, lines 355–398; `_core.py` public
entry options and `finish`, lines 624–682 and 704–759.

Problem / root cause: the new inner SchemaValidator calls receive neither the
outer strict/extra overrides nor its validation context. Only alias/name options
are carried across the boundary. The strings call receives caller input before
`finish` detaches it; the subsequent lambda ignores the detached input and returns
the already parsed model. Calling `finish` afterward cannot retroactively isolate
callbacks or restore lost options.

Evidence with Pydantic 2.13.4 controls:

- Strict JSON `{"value":"2"}` for an int field is rejected by BaseModel but
  accepted as `2` by DictModel.
- An extra-allow model entered with `extra="forbid"` rejects an extra in BaseModel
  but accepts it in DictModel.
- A field validator multiplying by context factor 3 returns `6` from BaseModel
  for input `2`, but `2` from DictModel because context is absent.
- A strings before-model validator edits `{"value":"2"}` to `{"value":"9"}`
  and raises. Validation fails but the caller's mapping remains edited.

Relationship to current change: all four behaviors were independently compared
to pre-remediation commit `0d1f231`; strict and extra reject, context produces 6,
and strings source remains `{"value":"2"}` there. They are introduced by the
SOL-017 remediation, not attributed to environment or unrelated nested support.
The original strict strings/date acceptance fixes are real but insufficient.

Why it matters / why this blocks: AC-001/020 require pinned strictness, applicable
entry options/context and detachment before callbacks. Accepting forbidden data,
silently changing validator outcomes or modifying caller-owned input on failure
breaks the public construction contract.

Required behavior / acceptance criteria: retain JSON/strings acceptance semantics
and strict Python rejection while preserving all applicable outer options and
context; detach input before any user validator. Retain annotation audits,
configured ongoing extra policy, nested ownership and canonical transaction
guarantees. Do not globally relax strictness or apply context after validation.

Verification artifact: `test_sol017_json_entry_options_match_pinned_basemodel`
(three distinct options) and
`test_sol017_rejected_strings_callback_cannot_mutate_entry_source` in the linked
new test file. Verification status: **CONFIRMED EXPECTED FAILURE**, four cases.
No new SOL ID is assigned to these manifestations of the unresolved replay root.

### SOL-015 — Qualification evidence is incomplete and not protected from invalid runs

Severity: **Medium**. Disposition: **BLOCKER**. Related AC: **AC-025/028**;
approved P5/P6 evidence work. AC-026's executable scalar oracle is now satisfied.

Location: `tools/qualify_package.py`, lines 286–315;
`docs/research/phase-0.3-results.json`, `phase-0.3-findings.md`;
qualification orchestration tests and remediation completion claims.

Problem: presence-only protected tests now pass, but the driver overwrites durable
records without validating source provenance. Existing successful mocked
qualification tests therefore publish simulated measurements into tracked
research files. The fresh package report maps only AC-024/025/028, not the required
full AC-to-test/lane inventory with stateful run/replay information, observed
failures and limitations. Its AC-025 reference `artifact_sha256` does not resolve
to a field; three specific hash fields exist instead.

Evidence: an independently passing full suite in the disposable candidate
checkout changed both tracked Phase 0.3 research records. JSON source_commit
became `""`; direct and rebuilt hashes both became
`b666e2c4d4b50237066cdaba2769f9ae8e9dd71b97c9ba9207f7ffe9e229fd20`, the SHA-256
of the protected test's `b"review artifact"`, not a measured wheel. A separate
isolated verification supplies successful commands without a source identity and
confirms an existing evidence record is overwritten.

The committed record itself has a nonempty, genuine measured source identity
`66be92f394a77f6dd94396c531831e3584443280`. Later candidate commits are docs-only;
that identity is not falsely classified as a source-code mismatch. Its real
commands/resolutions/hashes and the new scalar machine are acknowledged progress.

Relationship to current change: unconditional durable writes were added by this
remediation. This newly exposed corruption is part of SOL-015's same honest,
durable post-execution evidence contract, not a reopened historical SOL-008.
No original research file was allowed to be corrupted in the user's workspace.

Why it matters / why this blocks: AC-025 and P5 require reproducible, truthful
candidate evidence. A green regression suite that replaces measured provenance
with simulated success prevents trustworthy qualification and contradicts the
handoff's durability claim.

Required behavior / acceptance criteria: simulated/incomplete runs must not
replace verified records or present themselves as successful qualification;
missing/invalid provenance must fail or be explicitly non-qualifying. Isolate
test output from durable evidence. After real execution, retain valid measured
identity, interpreter/upstream resolutions, commands/artifacts, complete
AC-to-test/lane mapping, scalar settings/replay information and honest failure/
limitation reconciliation. Preserve historical records and keep local versus
all-platform proof distinct. No particular output schema or filename is required.

Verification artifact:
`test_sol015_missing_provenance_cannot_replace_durable_evidence` in the linked
new test file; isolated full-suite before/after record inspection. Verification
status: **CONFIRMED EXPECTED FAILURE**, one new case; real full-suite corruption
also reproduced. The original two presence tests pass and are not completeness
proof. Complete evidence content still requires manual re-review.

### SOL-016 — Installed metadata/dependency policy remains unverified

Severity: **Medium**. Disposition: **BLOCKER**. Related AC: **AC-024/028**, P5.

Location: `tools/qualify_package.py` bare/HTTP consumers and result collection,
lines 96–282; `pyproject.toml` project metadata.

Problem / evidence: the actual example now includes Mapping/MutableMapping
readers/writers, coupled success/rejection, reset, explicit metadata and independent
copy assertions. The driver copies and runs it outside the checkout in both bare
venvs with PYTHONPATH removed. This part is fixed. However, no executed consumer
or driver assertion reads and verifies the installed distribution's name,
version, license or exact Requires-Dist/runtime dependency policy. Twine checks
metadata validity, pip installs requirements, and freeze records resolutions;
none asserts those promised metadata values or absence of development-tool
runtime requirements. The py.typed check is retained and does verify the marker.

Relationship to current change: unresolved explicit requirement from the initial
SOL-016 finding, not a new package behavior defect. There is no evidence here that
the built package currently has incorrect metadata; the required verification is
missing. The remediation report claims full closure without addressing it.

Why it matters / why this blocks: AC-024 explicitly requires these installed
metadata and exact dependency-policy checks for direct and sdist-rebuilt wheels.
Source metadata inspection or an executable example cannot substitute for that
artifact-level gate.

Required behavior / acceptance criteria: verify the actual installed distribution
in each artifact path has the promised name `pydandict`, current project version
`0.2.0`, MIT license/license material, py.typed and exact runtime requirement
`pydantic==2.13.4`, without development-tool runtime requirements. Retain both
actual scalar examples and nested/HTTP/type consumers; record genuine outcomes.
No new version bump, license decision, broader dependency support or publication
is required.

Verification artifact / status: original protected orchestration case and fresh
real execution of both installed example paths **PASS**;
manual inspection of all emitted consumer programs and metadata-result fields
**CONFIRMS REMAINING OMISSION**. A static substring test is not added as a proxy
for real installed metadata verification. Automated artifact-level assertions
are required in remediation; their actual execution must be inspected at re-review.

## Quality gates and provenance

Reviewer runtime: macOS 26.5.2/arm64, CPython 3.11.14, Pydantic 2.13.4,
pydantic-core 2.46.4, Pyright 1.1.411. Candidate suite ran in detached disposable
checkout `/tmp/pydandict-rereview-6RWfRx/checkout`; pre-remediation controls ran
in its sibling `before-remediation`. Production commits were not modified.

| Gate actually executed | Result | Classification |
| --- | --- | --- |
| `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests -q --tb=short` in candidate checkout | 163 passed in 108.00s; includes all 7 protected Phase 0.3 cases and both state machines | PASS for executable checks; evidence files corrupted as SOL-015 describes |
| Same environment, new blocker test file, `-q --tb=short --show-capture=no` | 5 failed in 1.76s, all matching documented reasons | EXPECTED BLOCKER VERIFICATION |
| Pre-remediation/current public-entry differentials | Four formerly passing guarantees now fail | CHANGE-CAUSED; SOL-017 |
| Required Ruff check/format inventory | Pass; 26 candidate / 27 with new verification Python files formatted | PASS |
| `PYTHONPATH=src python tools/check_typing.py` in original workspace | Strict positive and exact negative diagnostics pass | PASS |
| Source `--verifytypes pydandict --ignoreexternal` | 100% public completeness; no errors | PASS |
| Source example | Executes successfully | PASS for source, not installed artifact proof |
| Docs checker before new report | 41 Markdown files, 255 links, 8 Python examples, zero errors | PASS |
| Fresh `python tools/qualify_package.py` attempt in isolated candidate | Build/Twine and direct bare example/consumer reached; direct HTTP installation fails with Errno 28, internal disk 188 MiB free | ENVIRONMENT; not a source defect or successful qualification |
| First external-drive qualification retry | Direct installed scalar/nested/HTTP consumers pass; Pyright reports assert_type unknown while discovering the old local Python default | ENVIRONMENT; explicit Python 3.11 PATH resolves it |
| Final fresh qualification with external temporary/cache space and explicit Python 3.11 first on PATH | Both actual installed examples, bare nested/HTTP consumers, marker, exact negative diagnostics and installed completeness pass | PASS for implemented checks; SOL-016 metadata assertions still absent |
| Final docs checker and diff check including review artifacts | 42 Markdown files, 259 links, 8 Python examples; zero errors; clean whitespace | PASS |
| Broader exploratory Ruff inventory including all tools/examples | Existing check_docs.py/probe_upstream.py import/format failures; both files unchanged from pre-remediation | PRE-EXISTING / OUTSIDE REQUIRED INVENTORY; no new blocker |
| First typing check in disposable checkout | Pyright chose Xcode Python 3.9 with old external Pydantic; two unknown PydanticExtraInfo diagnostics | ENVIRONMENT; verbose paths establish wrong interpreter; explicit 3.11 path passes with zero diagnostics |

Independently queried [CI run 34881387028](https://github.com/eddiethedean/pydandict/actions/runs/34881387028):
completed success at the exact candidate SHA. Eight runtime lanes (Ubuntu
3.11/3.12/3.13/3.14, macOS 3.11/3.14, Windows 3.11/3.14), two Ubuntu artifact
lanes (3.11/3.14) and docs all succeed. Push-only package preflight is skipped
as expected. This run predates the five new intentional verification failures;
its success is not asserted for the post-review worktree.

Successful fresh command: `python tools/qualify_package.py` in the disposable
candidate checkout, with `PATH` prefixed by
`/opt/homebrew/opt/python@3.11/libexec/bin`, `TMPDIR` set to
`/Volumes/T7/pydandict-rereview-ClFzxi` and `PIP_CACHE_DIR` to its `pip-cache`
subdirectory. This is a reviewer environment correction, not a production change.
Its 28 commands and full resolution records were written only in the disposable
checkout. Source identity is the exact candidate SHA. Measured hashes:

- sdist: `0c0a403ed8db2c4774074cc811b529b609aa37500d19550fb60683bfc956f319`.
- Direct wheel: `b4a950a317da1d10756bb5bae4a89a98fc9d2b6754b1df2b81d054f8f9bbea0d`.
- Rebuilt wheel: `1aed84b115e33f5a88a33ddacf3bfe0cf99a9eefa8f3d62cd99d4f4e6540e6cf`.

Both wheels are `pydandict-0.2.0-py3-none-any.whl`. Both bare resolutions contain
Pydantic 2.13.4, core 2.46.4, annotated-types 0.8.0, typing-inspection 0.4.4 and
typing_extensions 4.16.0. HTTP/type resolutions additionally include FastAPI
0.141.1, httpx 0.28.1, Pyright 1.1.411 and Starlette 1.6.0. These observations
establish actual local execution, not the missing explicit distribution-policy
assertions or an exhaustive fresh scalar leaf/mode matrix. The original user's
committed research files remain unchanged.

## Follow-ups and observations

Open GitHub issues were searched; no new unrelated defect needing an issue was
confirmed. SOL-011 remains **Low / FOLLOW-UP**, EXISTING ISSUE
[#2](https://github.com/eddiethedean/pydandict/issues/2), verified open. It does
not enter this remediation handoff. Issue #1 is separate existing security-policy
work. Exploratory historical-helper formatting and local interpreter/disk
conditions are observations, not new implementation requirements.

No arbitrary nested lifetime expansion, new timezone support, concurrency/
persistence work, numeric beta performance ceiling or repository-wide cleanup
is requested. This review did not collect a new scalar cost baseline or publish
anything; those activities must not be inferred from green tests.

## Convergence and handoff

Previous Phase 0.3 blockers resolved: **1 (SOL-014)**.
Remaining: **3 (SOL-015/016/017)**, all partially fixed.
New stable blocker IDs: **0**. Remediation introduced additional violations
within two existing blocker contracts (SOL-015 evidence integrity and SOL-017
entry semantics/isolation); these are documented without fragmenting root causes.
New unrelated follow-ups: **0**.

The loop is partially converging: bulk precedence, scalar oracle and actual
installed example are completed. Full convergence is not established while mode
replay trades old failures for new ones and qualification claims exceed its gates.
This is the first complete implementation attempt for these Phase 0.3 IDs; the
more-than-one-attempt escalation threshold is not yet met. A stronger replay/
options-and-detachment boundary and explicit non-durable test-output boundary
are the likely bounded solutions, not scope expansion.

Only SOL-015/016/017 go to implementation. Preserve all prior protected tests,
fix demonstrated options/isolation and evidence integrity, add the remaining
installed metadata gate, refresh truthful complete evidence, and re-review.

NEEDS FIXES
