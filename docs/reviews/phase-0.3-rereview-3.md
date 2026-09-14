# Phase 0.3 — Third independent production re-review

Reviewed 2026-09-14 against the [approved plan](../phase-0.3-plan.md),
[previous review](phase-0.3-rereview-2.md) and
[latest remediation report](phase-0.3-remediation-rereview-2.md).
Candidate: `5c72df2f2a6f6d3244810c39f2ef6a9d676f441e` on `main`, clean at entry.
The production remediation is `912b309350d94f75b8a8608f71c83b8d13132e05`;
the candidate's subsequent commit changes documentation only.
Only this report and [two blocker regression tests](../../tests/test_sol_phase03_rereview_3.py)
were added. Production, protected tests, workflows, dependencies and committed
qualification records remain unchanged. No commit, push or release was performed.

SOL-015 and SOL-017 remain PARTIALLY FIXED. The previous TypeAdapter strict JSON
rejection and the new implementation's extra-policy controls pass. However, the
replacement TypeAdapter path now rejects two previously accepted native-mode
inputs. The evidence map now names actual tests, but required non-applicable
cells and executed-lane reconciliation remain incomplete. No new finding ID is
needed for either unresolved root cause.

## Acceptance criteria

Retained VERIFIED statuses rely on prior contract inspection, inspection of this
remediation, the independently rerun complete candidate suite and exact-candidate
CI. They do not claim a newly exhaustive scalar leaf/mode matrix.

| AC | Status | Evidence / outstanding requirement |
| --- | --- | --- |
| AC-001 | REGRESSED | Class-method controls and strict TypeAdapter JSON rejection pass; strict strings and field-specific JSON strictness regress, SOL-017. |
| AC-002 | VERIFIED | Retained annotation/envelope, validator-output and hash-ingress controls pass; ingress audits remain. |
| AC-003 | VERIFIED | Retained ABC identity, canonical/default/excluded key and extra-order controls; installed scalar example passes. |
| AC-004 | VERIFIED | Retained read/membership/get/views/dict/pattern and serializer-separation controls pass. |
| AC-005 | VERIFIED | Retained iterator transition/invalidation controls pass; implementation unchanged. The new evidence anchor is incomplete, SOL-015. |
| AC-006 | VERIFIED | Protected-name, namespace and explicit class-entry alias controls pass. |
| AC-007 | VERIFIED | Scalar/bounds transaction controls and independent scalar oracle pass, including rejected writes. |
| AC-008 | VERIFIED | Batch/union/coupled validation and duplicate-precedence controls pass; scalar oracle compares atomic outcomes. |
| AC-009 | VERIFIED | Protected SOL-014 update/reset cases pass; staged name validation retains precedence. |
| AC-010 | VERIFIED | Existing-key/no-op and typed/unknown-extra setdefault controls pass. |
| AC-011 | VERIFIED | Destructive-operation controls and scalar extra-pop oracle pass; declared-field protection unchanged. |
| AC-012 | VERIFIED | Reset factory/deduplication/failure controls and scalar default/metadata oracle pass. |
| AC-013 | VERIFIED | Frozen write/missing/no-op controls pass; structural precedence does not relax freezing. |
| AC-014 | VERIFIED | Snapshot/fields-set controls and independent scalar values/order/metadata oracle pass. |
| AC-015 | VERIFIED | Canonical drift, programming-exception and mutation/copy context controls pass; transactions remain Python-mode and context-free. |
| AC-016 | VERIFIED | Reentry/prepared-swap/BaseException recovery and protected callback source-isolation controls pass. |
| AC-017 | VERIFIED | Computed-cache success/failure/no-op controls pass; commit/cache implementation unchanged. |
| AC-018 | VERIFIED | Copy ownership controls, scalar oracle and installed copy-independence example pass. |
| AC-019 | VERIFIED | Trusted-path rejection, deprecated-copy and inherited API controls pass. |
| AC-020 | REGRESSED | Protected class-method options/isolation and TypeAdapter strict JSON/extra controls pass; native TypeAdapter strings and field-specific strictness regress, SOL-017. |
| AC-021 | VERIFIED | Serializer/alias/exclusion/schema/context controls pass; serialization unchanged. |
| AC-022 | VERIFIED | Retained equality/hash controls pass; semantics unchanged. The new evidence anchor omits portions of this AC, SOL-015. |
| AC-023 | VERIFIED | Required strict typing inventory/exact negative diagnostics pass; public completeness 100%; both clean-wheel typing gates pass. |
| AC-024 | VERIFIED | Both fresh clean-wheel paths execute the actual scalar example and verify installed name/version/MIT license/dependency policy/py.typed without source injection. |
| AC-025 | PARTIALLY SATISFIED | Genuine local qualification and all advertised CI lanes pass; invalid-provenance preservation passes. Complete coverage/executed-lane reconciliation remains absent, SOL-015. |
| AC-026 | VERIFIED | Independent scalar values/order/fields-set oracle executes max_examples=100, stateful_step_count=100, deadline=None, derandomize=True; nested machine retained. |
| AC-027 | VERIFIED | All 170 existing candidate tests pass, including inherited nested and protected remediation controls. Newly added tests expose the separately identified AC-001/020 regression. |
| AC-028 | PARTIALLY SATISFIED | Actual installed example and docs gates pass; support boundary remains bounded. Required evidence inventory remains incomplete, SOL-015. |

## Previous blockers

| Finding | Status | Verification / root cause |
| --- | --- | --- |
| SOL-014 | VERIFIED FIXED | Protected bulk name-precedence tests pass; implementation unchanged. |
| SOL-015 | PARTIALLY FIXED | Provenance preservation, scalar proof and artifact gates pass. Actual test anchors are progress; non-applicable cells and actual executed-lane reconciliation remain missing. |
| SOL-016 | VERIFIED FIXED | Actual example and installed metadata assertions pass in both fresh bare wheel environments. |
| SOL-017 | PARTIALLY FIXED | All 13 prior Phase 0.3 blocker cases and related controls pass. New TypeAdapter branch introduces two confirmed native-mode regressions. |
| SOL-001 | VERIFIED FIXED | Retained annotation/generic/deferred completion controls pass. |
| SOL-002 | VERIFIED FIXED | Retained hash-ingress controls pass. |
| SOL-003 | VERIFIED FIXED | Retained owned-identity/ancestor-freeze controls pass. |
| SOL-004 | VERIFIED FIXED | Retained adapter shape/rebuild controls pass. |
| SOL-005 | VERIFIED FIXED | Required strict source inventory and exact negative diagnostics pass. |
| SOL-006 | VERIFIED FIXED | Both fresh direct/rebuilt qualification paths and advertised artifact CI lanes pass. |
| SOL-007 | VERIFIED FIXED | Retained benchmark baseline/generator contracts pass. |
| SOL-008 | VERIFIED FIXED | Historical benchmark provenance controls pass; SOL-015 remains the distinct current-phase evidence requirement. |
| SOL-009 | VERIFIED FIXED | Retained finalizer/disposal/prepared-swap controls pass. |
| SOL-010 | VERIFIED FIXED | Retained staging/callback reentry controls pass. |
| SOL-012 | VERIFIED FIXED | Protected existing-model Python context and class-method JSON context controls pass. |
| SOL-013 | VERIFIED FIXED | Protected existing-model Python ownership and strings source-isolation controls pass. |

## Remaining blockers

### SOL-017 — TypeAdapter fallback does not preserve native-mode validation semantics

Severity: High. Disposition: BLOCKER. Related AC: AC-001/020.
Location: `src/pydandict/_compat.py`, `wrap_model_schema`, lines 357–406.

Problem: the direct TypeAdapter branch first uses a Python-mode handler, then
selectively replays errors through a native-mode validator with global
`strict=True`. The error whitelist and unconditional strictness are not equivalent
to the original schema's native entry semantics. This remains the same
mode/options-preservation root cause as SOL-017.

Evidence, differential against pinned Pydantic 2.13.4:

- An integer field entered through `TypeAdapter.validate_strings({"value":"2"},
  strict=True)` is accepted as `2` by BaseModel, but DictModel raises `int_type`.
  The first Python-mode error is excluded from the replay whitelist.
- A strict date field alongside a normal integer field entered through
  `TypeAdapter.validate_json('{"date_value":"2026-01-01","count":"2"}')`
  produces a date and integer `2` in BaseModel. DictModel's date replay makes the
  normal integer field globally strict and raises `int_type` for `count`.

Relationship to current change: both DictModel inputs were independently accepted
at prior candidate `6dc29084b92d8663b5049e6e8c609be417f73c71`. Their rejection is
attributable to remediation `912b309`, not an unrelated pre-existing defect.
The previous strict JSON rejection is now fixed; the new extra-policy test also
passes. Fixing those symptoms has not closed the native-mode invariant.

Why it matters / why this blocks this change: AC-001/020 explicitly include
TypeAdapter, applicable entry flags and native Python/JSON/strings behavior.
Rejecting supported inputs breaks this change's public compatibility guarantee.
These are distinct native-mode and field-specific strictness regressions, not
additional equivalent permutations or expanded nested scope.

Required behavior / acceptance criteria: preserve pinned native-mode acceptance
and rejection, including strict strings and field-specific versus call-level
strictness, across TypeAdapter and class methods. Retain extra/alias/context
behavior, source detachment, canonical transactions and nested ownership. No
particular implementation or exact validator callback count is prescribed.

Verification artifact: `tests/test_sol_phase03_rereview_3.py`, both tests.
Verification status: CONFIRMED EXPECTED FAILURE, two `int_type` errors after the
BaseModel controls succeed. All 24 protected and related compatibility cases pass.

ESCALATION RECOMMENDED: this blocker survives three remediation attempts.
Architectural reconsideration of the native-mode schema boundary is indicated;
exception-type replay is not a sufficient model for preserving entry semantics.
No specification or environmental clarification is needed to reproduce it.

### SOL-015 — Coverage anchors still do not complete the required evidence inventory

Severity: Medium. Disposition: BLOCKER. Related AC: AC-025/028; approved P1/P5/P6.
Location: `tools/qualify_package.py`, `_AC_TEST_LANE_MAP` and record generation;
`docs/research/phase-0.3-results.json` and its readable companion.

Problem: records now list test anchors for all 28 ACs and the readable companion
includes them. They still lack explicit non-applicable matrix cells and an
auditable reconciliation to actual external runtime/docs/CI executions. Runtime
entries say only `CI compatibility matrix` and `required external runtime gate;
recorded separately from this artifact driver`, without identifying those
recorded executions. No complete reconciled matrix was found elsewhere.

Evidence: manual comparison with approved P1/P5/P6 and inspection of both the
committed and independently regenerated records. Some genuine anchors also fail
to demonstrate the complete criterion: AC-005 names a mapping-view test, not its
iterator transition/invalidation controls; AC-022 names a stale-child test that
does not cover mutable/frozen hashing and model-versus-dict equality. Passing
those nodes is not complete proof of the advertised AC. Existing runtime controls
are acknowledged; this is an incomplete qualification inventory, not a newly
asserted runtime defect in AC-005/022.

Relationship to current change: this is the same required evidence deliverable
identified in SOL-015. Invalid-provenance protection, stateful settings,
failures/limitations and actual clean artifact execution remain verified fixed.
Real node anchors are useful progress; their presence alone does not establish
coverage or executed-lane reconciliation.

Why it matters / why this blocks this change: the approved qualification/handoff
gate requires an AC inventory with actual proof nodes, relevant matrix cells,
explicit non-applicability and reconciliation after execution. Genuine green CI
does not replace that separate deliverable. The remediation's full-closure claim
is premature; no invented output schema or repository-wide perfection is required.

Required behavior / acceptance criteria: supply an auditable complete inventory
using actual existing/new proof nodes, applicable cells and explicit exclusions;
tie genuine runtime/stateful/docs/artifact/CI execution to candidate identity,
commands/resolutions, failures and limitations. Referencing existing actual run
records is sufficient; the artifact driver need not execute every gate. Preserve
historical evidence and non-qualifying-run protection. Do not label unverified
cells as passing.

Verification artifact: manual content audit described above, with the protected
provenance test and fresh qualification run. Verification status: CONFIRMED
INCOMPLETE. No brittle schema-prescribing failing test was added.

ESCALATION RECOMMENDED: this requirement survives three remediation attempts.
A stronger coverage/evidence model is needed. The specification already states
the requirement; no external clarification is necessary.

## Verification and provenance

Existing-suite and artifact checks used a detached exact-candidate worktree at
`/Volumes/T7/pydandict-sol-third-cOhhBy/checkout`; prior-candidate differential
checks used its sibling `previous` worktree. Fresh qualification records remain
in the detached checkout, leaving the user's committed records untouched.
The committed records identify production commit `912b309`; the following
docs-only commit is not falsely classified as a production-source mismatch.

- Complete existing candidate suite: 170 passed in 104.57s.
- Protected and related compatibility tests: 24 passed in 0.21s, including all
  13 prior Phase 0.3 blocker cases and the latest implementation regression test.
- New blocker tests: 2 expected failures in 0.26s, attributable to this remediation.
- Required Ruff inventory/formatting: pass; new verification file also clean.
- Strict positive/negative typing helper: pass, exact inventory/diagnostics.
- Public completeness: 100%, no errors; both installed artifact gates also pass.
- Candidate docs: 45 Markdown files, 265 local links, 8 Python examples, 0 errors.
- Docs including this review: 46 Markdown files, 269 local links, 8 Python
  examples, 0 errors; whitespace check passes.
- Fresh direct/sdist-rebuilt qualification: pass, including actual scalar example,
  metadata/license/dependencies/py.typed, nested/HTTP consumers, strict installed
  typing/completeness and exact four negative diagnostics.

Fresh artifact run: source `5c72df2f2a6f6d3244810c39f2ef6a9d676f441e`, Python
3.11.14, macOS 26.5.2 arm64; resolved Pydantic 2.13.4 / pydantic-core 2.46.4,
FastAPI 0.141.1, HTTPX 0.28.1, Starlette 1.6.0 and Pyright 1.1.411.
Both bare wheel environments recorded `metadata verified`.

| Artifact | SHA-256 |
| --- | --- |
| sdist | `974367ef83c274ac51e9454b4d8e645fb72b4aa6589f2ed258a04bf5538a90a7` |
| direct wheel | `23fec029c9de362b040d75f8ab5393715e296c39e5cb980cae13a4aea6e790c9` |
| sdist-rebuilt wheel | `8441fbadd89cbdb64f6e7c3b423d4d9f50db6d26d7ee421d0f686d339a82da2e` |

Commands: `python -m pytest -q`, with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and
`PYTHONPATH=src`; focused prior/new test files; CI's exact Ruff inventory;
`python tools/check_typing.py`; `python -m pyright --verifytypes pydandict
--ignoreexternal`; `python tools/check_docs.py`; `python tools/qualify_package.py`
with Python 3.11 first in PATH and external TMPDIR/cache. Artifact execution clears
PYTHONPATH and installs in isolated environments outside the checkout.

[Exact-candidate CI](https://github.com/eddiethedean/pydandict/actions/runs/34888302784)
is completed/success: eight runtime lanes (Ubuntu 3.11/3.12/3.13/3.14,
macOS 3.11/3.14, Windows 3.11/3.14), two Ubuntu artifact lanes (3.11/3.14),
and documentation. Release-only preflight is appropriately skipped on push.
This run predates the two new failing tests; it does not demonstrate closure of
their invariant or green CI for the newly added review artifacts.

Environmental limitations: local checks cover macOS/Python 3.11; other advertised
lanes were independently verified through CI, not simulated locally. An initial
new-file lint invocation used a nonexistent `uv` path and did not execute lint;
the installed `ruff` executable subsequently passed both checks. No environmental
failure is being used to excuse either blocker.

## Follow-ups, observations and convergence

SOL-011 remains Low / FOLLOW-UP, related AC: NONE, outside this scalar change.
GitHub status: EXISTING ISSUE #2,
[“Investigate repeated root after-validator invocation on recursive DictModel schemas”](https://github.com/eddiethedean/pydandict/issues/2).
Open issues were searched; no duplicate issue or intentionally failing follow-up
test was created. No new unrelated follow-up or observation is handed to remediation.

Previous blockers newly closed: none. SOL-014 and SOL-016 remain closed.
Blockers remaining: SOL-015 and SOL-017, both PARTIALLY FIXED.
New independent blocker IDs: none. Two regressions attributable to the latest
remediation remain within SOL-017. The evidence anchors and strict JSON/extra
improvements are real, but the loop has not yet converged: native-mode compatibility
has traded one failure for another. Escalate both repeated blockers as above.
Only SOL-015/017 enter implementation; follow-ups do not prevent approval.

Verdict: NEEDS FIXES.
