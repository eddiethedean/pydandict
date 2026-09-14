# Phase 0.3 — Second independent production re-review

Reviewed 2026-09-14 against the [approved plan](../phase-0.3-plan.md),
[initial review](phase-0.3-review.md), [first re-review](phase-0.3-rereview.md)
and [latest remediation report](phase-0.3-remediation-rereview.md).
Candidate: `6dc29084b92d8663b5049e6e8c609be417f73c71` on `main`, clean at entry.
Only this report and the linked [blocker test](../../tests/test_sol_phase03_rereview_2.py)
were added. Production code, protected prior tests, workflows, dependencies and
the user's qualification records remain unchanged. No commit, push or release
was performed.

SOL-016 is now verified fixed. SOL-015 and SOL-017 remain partially fixed.
The twelve previous Phase 0.3 blocker cases pass; the new TypeAdapter contract
fails for the expected reason. Exact-candidate CI is genuinely green, but does
not cover this remaining entry-options invariant or supply the required complete
AC-to-test-node evidence inventory.

## Acceptance criteria

These are Phase 0.3 IDs. Retained VERIFIED statuses use prior contract inspection,
inspection of the remediation, the independently rerun complete candidate suite
and exact-candidate CI; they do not claim a new exhaustive leaf/mode matrix.

| AC | Status | Evidence / outstanding requirement |
| --- | --- | --- |
| AC-001 | PARTIALLY SATISFIED | Prior strict strings/JSON controls and class-method overrides pass; TypeAdapter strict JSON coercion still violates pinned-schema behavior, SOL-017. |
| AC-002 | VERIFIED | Retained envelope/annotation, validator-output and hash-ingress controls pass; construction/copy/commit audits remain. |
| AC-003 | VERIFIED | Retained ABC identity, canonical/default/excluded keys and extra-order controls; actual installed example uses mapping readers/writers. |
| AC-004 | VERIFIED | Read/membership/get/views/dict/pattern and serializer-separation controls pass; installed example remains public-API-only. |
| AC-005 | VERIFIED | Iterator transition/invalidation controls pass; iterator implementation unchanged. |
| AC-006 | VERIFIED | Retained protected-name, namespace and explicit class-entry alias controls pass. |
| AC-007 | VERIFIED | Scalar/bounds transaction controls and independent scalar oracle pass, including rejected writes. |
| AC-008 | VERIFIED | Batch/union/coupled validation and duplicate-precedence controls pass; scalar oracle compares atomic outcomes. |
| AC-009 | VERIFIED | SOL-014 protected bulk precedence cases pass; complete staged name checks still precede policy. |
| AC-010 | VERIFIED | Retained existing-key/no-op and typed/unknown-extra setdefault controls pass. |
| AC-011 | VERIFIED | Destructive-operation inventory and scalar extra-pop oracle pass; declared-field protections unchanged. |
| AC-012 | VERIFIED | Reset factory/deduplication/failure controls pass; scalar oracle independently tracks defaults and explicit metadata. |
| AC-013 | VERIFIED | Frozen write/missing/no-op controls pass; bulk structural precedence does not relax freezing. |
| AC-014 | VERIFIED | Snapshot/fields-set controls and independent scalar values/order/metadata oracle pass; example checks reset/removal. |
| AC-015 | VERIFIED | Canonical drift, programming-exception and mutation/copy context controls pass; transaction validation remains Python-mode and context-free. |
| AC-016 | VERIFIED | Retained reentry/prepared-swap/BaseException recovery controls pass; strings entry source-isolation regression is fixed. |
| AC-017 | VERIFIED | Computed-cache success/failure/no-op controls pass; commit/cache implementation unchanged. |
| AC-018 | VERIFIED | Parametrized copy ownership, scalar oracle and installed example copy-independence controls pass. |
| AC-019 | VERIFIED | Trusted-path rejection, deprecated-copy and inherited API controls pass. |
| AC-020 | PARTIALLY SATISFIED | Class-method strict/extra/context and callback isolation now pass; TypeAdapter strict/extra overrides still disappear, SOL-017. |
| AC-021 | VERIFIED | Retained serializer/alias/exclusion/schema/context controls pass; serialization unchanged. |
| AC-022 | VERIFIED | Retained equality/hash controls pass; semantics unchanged. |
| AC-023 | VERIFIED | Required strict source inventory/exact negative diagnostics pass; public completeness 100%; both fresh wheel typing gates pass. |
| AC-024 | VERIFIED | Both fresh clean-wheel paths execute the actual scalar workflow and assert installed name/version/MIT license/runtime dependency policy/py.typed without source injection. |
| AC-025 | PARTIALLY SATISFIED | All advertised CI lanes pass; genuine local provenance exists and invalid-run preservation is fixed. Complete executed AC-to-test/lane reconciliation remains absent, SOL-015. |
| AC-026 | VERIFIED | Independent scalar values/order/fields-set oracle executes max_examples=100, stateful_step_count=100, deadline=None, derandomize=True; nested machine retained. Settings are now recorded. |
| AC-027 | VERIFIED | Complete candidate regression suite passes, including inherited nested and protected prior remediation controls. |
| AC-028 | PARTIALLY SATISFIED | Actual installed example and docs checks pass; support boundary remains bounded. Required evidence inventory is incomplete, SOL-015. |

## Previous blockers

| Finding | Status | Verification / root-cause inspection |
| --- | --- | --- |
| SOL-014 | VERIFIED FIXED | Both protected update/reset cases pass; staged non-string names still take precedence without committing. |
| SOL-015 | PARTIALLY FIXED | Scalar proof and invalid-provenance preservation pass; real records include settings/failures/limitations. Generic suite labels still do not implement required test-node coverage/evidence reconciliation. |
| SOL-016 | VERIFIED FIXED | Actual example runs in both wheels; new installed metadata assertions execute successfully in both bare environments. |
| SOL-017 | PARTIALLY FIXED | All six prior mode/options/isolation cases pass. TypeAdapter bypasses the new class-method option boundary, so its JSON strict/extra overrides remain lost. |
| SOL-001 | VERIFIED FIXED | Retained annotation/generic/deferred completion controls pass. |
| SOL-002 | VERIFIED FIXED | Retained hash-ingress controls pass. |
| SOL-003 | VERIFIED FIXED | Retained owned-identity/ancestor-freeze controls pass. |
| SOL-004 | VERIFIED FIXED | Retained adapter shape/rebuild controls pass. |
| SOL-005 | VERIFIED FIXED | Required strict source inventory and exact negative diagnostics pass. |
| SOL-006 | VERIFIED FIXED | Both real direct/rebuilt qualification paths and advertised artifact CI lanes pass. |
| SOL-007 | VERIFIED FIXED | Retained benchmark baseline/generator contracts pass. |
| SOL-008 | VERIFIED FIXED | Historical benchmark provenance controls pass; SOL-015 remains the distinct current-phase evidence deliverable. |
| SOL-009 | VERIFIED FIXED | Retained finalizer/disposal/prepared-swap controls pass. |
| SOL-010 | VERIFIED FIXED | Retained staging/callback reentry controls pass. |
| SOL-012 | VERIFIED FIXED | Protected existing-model Python context controls pass; latest class-method JSON context regression also fixed under SOL-017. |
| SOL-013 | VERIFIED FIXED | Protected existing-model Python ownership controls pass; latest strings source mutation also fixed under SOL-017. |

## Remaining blockers

### SOL-017 — Replacement mode validator still loses TypeAdapter entry options

Severity: High. Disposition: BLOCKER. AC-001/020.

Location: `src/pydandict/_compat.py`, `wrap_model_schema` lines 357–405;
`src/pydandict/_core.py`, public validation class-method entry boundary.

Root cause: JSON/strings use a replacement SchemaValidator. Strict/extra overrides
are now transported through `_ENTRY_OPTIONS`, but only the DictModel class
methods establish that context. TypeAdapter enters the model schema directly.
The fallback supplies `None` for strict and extra, so the inner validator uses
model configuration rather than the applicable outer request. This is the same
unresolved option-preservation root cause, not a new finding or scalar scope
expansion: AC-020 explicitly includes TypeAdapter.

Confirmed differential with Pydantic 2.13.4:

- `TypeAdapter(Record).validate_json('{"value":"2"}', strict=True)` with an int
  field: BaseModel rejects with `int_type`; DictModel accepts and stores `2`.
- With `extra="allow"` configuration, JSON `{"value":2,"other":3}` entered
  through TypeAdapter with `extra="forbid"`: BaseModel rejects with
  `extra_forbidden`; DictModel accepts the extra.

The new test
`tests/test_sol_phase03_rereview_2.py::test_sol017_type_adapter_strict_json_matches_pinned_basemodel`
first proves the pinned BaseModel rejection, then fails on DictModel with
`DID NOT RAISE ValidationError`. Verification: CONFIRMED EXPECTED FAILURE.
One representative automated case is sufficient; the extra-policy differential
was checked manually rather than adding equivalent symptom permutations.

Why this blocks this change: AC-001/020 require schema strictness and applicable
public entry flags, explicitly including TypeAdapter. Silently accepting forbidden
input breaks the changed construction/compatibility guarantee. Passing the
class-method-only tests cannot establish the framework-level entry contract.

Required behavior: preserve applicable options across all supported public entry
paths, including TypeAdapter, while retaining original strict JSON/strings mode
acceptance, strict Python rejection, aliases/context and detachment before user
callbacks. Preserve configured ongoing extras, canonical transactions and nested
ownership. The verification does not prescribe a particular implementation.

ESCALATION RECOMMENDED: this root cause survives two implementation attempts.
Architectural reconsideration of the mode-preserving schema boundary is indicated;
an option bridge limited to class methods cannot cover direct framework entry.
No specification or environmental clarification is needed to reproduce the failure.

### SOL-015 — Required AC-to-test-node/executed-lane inventory is still incomplete

Severity: Medium. Disposition: BLOCKER. AC-025/028; approved P1/P5/P6 evidence work.

Location: `tools/qualify_package.py`, `_AC_TEST_LANE_MAP` lines 29–69 and durable
record generation; `docs/research/phase-0.3-results.json` and its readable companion.

Fixed portions: invalid/missing Git identity produces an explicitly non-qualifying
result without overwriting evidence; the protected sentinel test passes. Fresh
real qualification succeeds. Scalar profile settings, observed-failure and
limitation fields are now present and correctly distinguish local artifact
execution from external runtime/docs gates.

Unresolved requirement: P1 explicitly requires an AC inventory with existing/new
test node IDs and explicit non-applicable matrix cells. P5/P6 require AC-to-test/
lane proof and reconciliation after execution. AC-001 through AC-023 all receive
the identical `tests/ (full runtime suite)` label and `CI compatibility matrix`
lane description. These are required target labels, not an inventory identifying
which executable cases prove each criterion or which cells are non-applicable.
The readable companion lists only AC-024/025/026/028 and does not reconcile the
full runtime/matrix results. No complete Phase 0.3 inventory was found elsewhere.

Manual verification: compare the current machine/readable evidence with approved
P1 lines 380–390, P5 lines 434–451 and P6 lines 460–473. The record's 28 keys pass
presence checks, but the required test-node/executed-lane content remains missing.
This manual audit was explicitly left outstanding by the prior re-review; no
brittle output-schema test was added to enforce a particular representation.

Why this blocks this change: it leaves the approved qualification/handoff gate
incomplete and cannot explain untested compatibility cells, such as the confirmed
TypeAdapter defect. Genuine green full-suite/CI execution is acknowledged, not
reclassified as failure; it does not replace the separately required coverage
and evidence deliverable. The remediation report's full-closure claim is premature.

Required behavior: provide an auditable complete AC inventory tied to actual
existing/new test nodes, relevant matrix cells and explicit non-applicability;
reconcile real runtime/stateful/docs/artifact/CI execution with candidate identity,
commands/resolutions, failures and limitations. Referencing existing genuine
run records is sufficient; the package driver need not execute every gate or
use any prescribed output schema. Preserve non-qualifying-run protection and
historical records. Do not invent passing coverage for unverified cells.

ESCALATION RECOMMENDED: the same evidence-completeness requirement survives two
implementation attempts. A stronger evidence/coverage model is needed, not more
generic AC labels. The approved specification already states the requirement.

## Verification and provenance

Checks used a detached exact-candidate worktree at
`/Volumes/T7/pydandict-sol-rereview-QL053o/checkout`. Fresh artifact output stayed
there, preserving the user's committed research records. The committed artifact
identity `b8ff5071d215baca6c44a109ba6d0ebbae627ded` precedes docs-only commits;
it is not falsely reported as a production-source mismatch.

- Twelve prior Phase 0.3 blocker cases: 12 passed in 0.40s.
- Complete exact-candidate suite: 168 passed in 104.82s, including protected
  benchmark/provenance checks and both scalar/nested state machines.
- New TypeAdapter blocker case: 1 expected failure in 0.27s.
- Required Ruff inventory and formatting: pass; new verification file also clean.
- Strict positive/negative typing helper: pass with exact source inventory and diagnostics.
- Public completeness: 100%, no errors; both installed artifact gates also pass.
- Candidate docs: 43 Markdown files, 260 local links, 8 Python examples, 0 errors.
- Docs including this review: 44 Markdown files, 265 local links, 8 Python examples,
  0 errors; whitespace check passes.
- Fresh direct/sdist-rebuilt qualification: pass, including actual example,
  installed metadata/license/dependencies/py.typed, nested/HTTP consumers,
  strict installed typing/completeness and exact four negative diagnostics.

Fresh artifact run: Python 3.11.14, macOS 26.5.2 arm64, source
`6dc29084b92d8663b5049e6e8c609be417f73c71`; resolved Pydantic 2.13.4 /
pydantic-core 2.46.4, FastAPI 0.141.1, HTTPX 0.28.1, Pyright 1.1.411.
Both bare environments recorded `metadata verified`.

| Artifact | SHA-256 |
| --- | --- |
| sdist | `17b801feb6d58dd60839b00b78569d62f2a4abbf91562d342e9529e3b4fe0b57` |
| direct wheel | `c26e15b2373cab808fd599e3d3bf19d63bae1008610d70367e1e56e0de2d1382` |
| sdist-rebuilt wheel | `7838aaf692d2074930fe1e00c5ebf2400aa439d05abfa8acebbfe137821458d9` |

Commands: `python -m pytest -q` with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and
`PYTHONPATH=src` for source tests; the focused prior/new test paths above;
CI's exact Ruff inventory; `python tools/check_typing.py`;
`python -m pyright --verifytypes pydandict --ignoreexternal`;
`python tools/check_docs.py`; `python tools/qualify_package.py` with external
TMPDIR/cache and Python 3.11 first in PATH. Qualification clears PYTHONPATH and
installs into isolated environments outside the checkout.

[Exact-candidate CI](https://github.com/eddiethedean/pydandict/actions/runs/34884896129)
is completed/success: eight runtime lanes (Ubuntu 3.11/3.12/3.13/3.14,
macOS 3.11/3.14, Windows 3.11/3.14), two Ubuntu artifact lanes (3.11/3.14),
and documentation. Release-only preflight is appropriately skipped on push.
This run predates the newly added failing test; it is not green CI for the review
artifact or proof that SOL-017 is closed.

Environmental limitations: the first local pytest invocation was stopped before
collection by an unrelated globally installed pytest-cases plugin incompatible
with local pytest. Re-running with CI's plugin-autoload setting removes that
environmental problem. These are source checks on macOS/Python 3.11; other lanes
are independently verified through the CI run rather than simulated locally.

## Follow-ups and observations

SOL-011 remains Low / FOLLOW-UP, outside this scalar change:
[existing open issue #2](https://github.com/eddiethedean/pydandict/issues/2),
“Investigate repeated root after-validator invocation on recursive DictModel schemas”.
Open issues were searched; no duplicate issue or intentionally failing follow-up
test was created. No new worthwhile unrelated defect was found.

Low / OBSERVATION: an exploratory Ruff run broader than the required inventory
finds import-order warnings in unchanged `tools/check_docs.py` and
`tools/probe_upstream.py`. Required Ruff gates pass. This minor pre-existing
cleanup is not a release requirement and is not sent to implementation.

## Convergence and verdict

Previous blockers newly resolved: SOL-016. SOL-014 remains closed.
Blockers remaining: SOL-015 and SOL-017, both PARTIALLY FIXED.
New independent blocker IDs: none. New unrelated follow-ups: none.
The class-method option/source-isolation and installed metadata improvements are
real, so the loop is converging, but repeated partial closure merits escalation.
Only the two BLOCKER contracts above enter remediation; follow-ups/observations
do not. Approval does not require repository-wide perfection or publication.

Verdict: NEEDS FIXES.
