# Phase 0.3 — Third re-review remediation report

Scope: only SOL-015 and SOL-017 from the complete
[latest Sol review](phase-0.3-rereview-3.md), against the
[approved contract](../phase-0.3-plan.md). Base: `5c72df2` on `main`.
The prior review and its untracked regression file were preserved unchanged.
No production module, dependency, workflow or protected verification was modified.
No commit, push, publication, FOLLOW-UP fix or gate suppression occurred.

This is a partial remediation with a deliberate escalation, not another full-closure
claim. The evidence helper and implementation-side proof improve SOL-015; SOL-017
requires architectural assessment before another safe implementation attempt.

## SOL-015 — Coverage anchors still do not complete the required evidence inventory

Status: PARTIALLY FIXED

Related AC: AC-025/028; approved P1/P5/P6.

Root cause: the helper recorded representative node labels and generic external
lane descriptions without actual execution reconciliation, complete applicability
or complete coverage proof. Its mapping-view and stale-child anchors did not prove
AC-005/022. It also accepted a valid HEAD identity even when relevant uncommitted
source/test/tool files differed from that commit.

Production changes: `tools/qualify_package.py`, `_coverage`, `_AC_TEST_LANE_MAP`,
`qualifying_source` and `main`:

- Identify all eleven advertised CI cells for each AC, with explicit applicable
  versus non-applicable job status and reasons; distinguish docs from runtime jobs.
- Extend relevant anchors and replace AC-005/022's misleading anchors with direct
  scalar iterator and equality/hash proof.
- Preserve durable records when relevant files differ from HEAD, as well as when
  Git identity is missing. Retain actual artifact measurements, commands, upstream
  resolutions and worktree status in non-qualifying output without claiming closure.
- Reference separate bounded execution evidence with explicit source-comparison
  requirements; merely finding that record is not a passing gate.

Before-fix verification: Sol's manual content audit found missing non-applicable
cells/executed-lane reconciliation and incomplete AC-005/022 anchors. The protected
missing-provenance test already passed; valid HEAD with dirty test/tool source was
not protected by the prior implementation.

After-fix verification: manual inspection of the new helper and separate
[readable reconciliation](../research/phase-0.3-remediation-3-findings.md) /
[machine evidence](../research/phase-0.3-remediation-3-evidence.json) confirms
28 AC entries, all eleven advertised job cells, actual historical job URLs and
resolved Python patch versions, current local node outcomes and exact source
file hashes. All listed pytest selectors resolve in collection. AC-027 expands
the entire 170-test retained inventory. The protected provenance sentinel and
orchestration tests pass. Two real dirty-worktree artifact runs report
`non-qualifying` and leave prior durable qualifying records unchanged.

Related regression tests: all three prior Phase 0.3 blocker files and
`tests/test_compat_remediation.py`, together with the new implementation tests:
27 passed. Full suite: 173 passed, two open SOL-017 failures.

Additional tests: `tests/test_phase03_evidence_contract.py`:

- Iterator creation-before-first-next, value-only/failure/no-op stability,
  structural removal/reinsertion invalidation and permanent exhaustion.
- Model-versus-model/dict equality, mutable unhashability and frozen scalar hash
  differential against a pinned BaseModel control, including allowed extras.
- Missing/dirty source-identity rejection in the helper; actual orchestration also
  verifies non-qualifying output without replacing durable evidence.

Resolution: PARTIAL. Job-level applicability and observed execution reconciliation
are now explicit, and the two specific misleading anchors are corrected. These
do not substitute for the full behavioral leaf/annotation/entry-mode and
mutator-policy/freeze coverage audit, including behavioral non-applicable cells.
That audit remains outstanding. Current all-platform CI has not executed these
uncommitted tests/tool changes; historical successful CI is not current-candidate
proof. A qualifying durable refresh must follow a correct SOL-017 repair and
clean candidate execution. SOL-015 is not reported closed.

## SOL-017 — TypeAdapter fallback does not preserve native-mode validation semantics

Status: ESCALATION REQUIRED

Related AC: AC-001/020.

Root cause: `wrap_model_schema` sends cloned Python values through the wrap
handler, losing native JSON/StringInput behavior. Direct TypeAdapter entry does
not establish the class-method `_ENTRY_OPTIONS` context, and ValidationInfo does
not expose dynamic strict/extra options. The remediation tries to recover native
behavior by classifying exceptions and replaying with global `strict=True`.
That loses both strict strings coercion and field-specific versus call-level
strictness. The prior class-method bridge could not cover TypeAdapter; the latest
exception whitelist traded strict JSON/extra failures for new acceptance failures.

Production changes: none. No additional whitelist, guessed strictness, callback
replay or replacement validator was introduced. No speculative implementation
was left in the tree.

Before-fix verification: both tests in `tests/test_sol_phase03_rereview_3.py`
fail after their pinned BaseModel controls accept the input: `int_type` for
strict strings `value`, and `int_type` for the ordinary `count` field next to a
strict JSON date. Targeted run: two failures in 0.16s.

After-fix verification: no fix is claimed. The same protected tests fail for
the same reasons in the complete run: two failures, 173 passes in 101.67s.

Related regression tests: all 13 prior Phase 0.3 blocker cases and related
TypeAdapter/class-method/cache/deferred-schema controls pass in the 27-test
focused run. Existing ownership, nested, transaction and stateful tests pass
in the complete run. Source isolation cannot be relaxed to obtain green modes.

Additional tests: no new equivalent SOL-017 permutations were added. Read-only
standalone SchemaValidator probes compared native strict date validation with
identity before/wrap/chain callbacks in JSON and strings modes. Native validation
accepts the date string; each Python callback boundary reproduces `date_type`.
Simply splitting the current wrap into before/after or chain hooks is not enough.
The native strictness distinction is also documented in
[Pydantic's strict-mode contract](https://github.com/pydantic/pydantic/blob/main/docs/concepts/strict_mode.md).

Resolution: ESCALATION REQUIRED. The current `finish(value, next_validator, ...)`
abstraction couples pre-callback source isolation, schema validation and ownership
installation around a Python handler. The needed design must preserve native
input and caller options while isolating strings/existing-model inputs before
callbacks and retaining canonical Python transactions. Moving finalization to an
after hook alone does not establish those isolation/ownership invariants. I cannot
confidently implement that boundary change as another ordinary bounded patch.

Requested architectural assessment: Sol should approve a native-mode-preserving
adapter ingress/validation/finalization boundary and its source-isolation proof
before another implementation attempt. Determine whether framework-native hooks
can meet both requirements or whether an upstream limitation requires an explicit
architecture decision. No dependency expansion, monkey patch, external plugin,
engine rewrite or specification relaxation has been silently adopted. The
verification is valid and remains intact; this is not a VERIFICATION CONFLICT.

## Follow-Up report

Existing Sol FOLLOW-UP: SOL-011, repeated root-after callback invocation on recursive
schemas, remains outside this scalar remediation in
[existing issue #2](https://github.com/eddiethedean/pydandict/issues/2).
It was not fixed or turned into a required failing test.
New FOLLOW-UP candidates: none. Observations: none implemented.

## Quality gate report

Only executed results are claimed. See the separate machine record for commands,
source hashes, expanded nodes, upstream versions and measured artifact identities.

| Gate | Executed | Result | Notes |
| --- | --- | --- | --- |
| New protected SOL-017 tests | Yes | FAIL — OPEN BLOCKER | Both fail with the expected `int_type` errors; verification preserved. |
| Protected/related compatibility plus implementation proof | Yes | PASS | 27 passed in 0.33s; all prior Phase 0.3 cases included. |
| Complete runtime suite | Yes | FAIL — OPEN BLOCKER | 173 passed, 2 failed in 101.67s; only SOL-017 fails. |
| Inventory collection audit | Yes | PASS | 175 collected nodes, no unmatched pytest selectors; not a complete semantic coverage audit. |
| Required Ruff lint | Yes | PASS | Full required source/test/tool inventory. |
| Required formatting | Yes | PASS | 30 files formatted. |
| Strict positive/exact negative typing | Yes | PASS | Required production inventory and diagnostic rules/locations. |
| Public completeness | Yes | PASS | 100%, no errors. Pinned Pyright retained despite upgrade notice. |
| Direct/rebuilt clean-wheel consumer exercises | Yes | PASS | Actual scalar example, metadata/MIT/dependencies/py.typed, nested/HTTP and installed typing gates. |
| Durable qualifying artifact refresh | Yes | FAIL — OPEN BLOCKER | Non-qualifying dirty snapshot; prior evidence preserved. Artifact exercise success is not full qualification. |
| Historical base-commit CI inspection | Yes, read-only | PASS | Eleven successful jobs at `5c72df2`, exact interpreter patches/resolutions read from logs; release preflight skipped appropriately. |
| Current all-platform candidate CI | No | NOT RUN — ENVIRONMENTAL/UNAVAILABLE | No committed/pushed candidate and no authorized CI dispatch; historical CI is not substituted. |
| Documentation / whitespace | Yes | PASS | 48 Markdown files, 274 local links, 8 Python examples, no errors; diff whitespace clean. |

No full qualification, green current CI or independent approval is claimed.
No production correction was shipped while the native-mode boundary remained
uncertain. Changes to the evidence helper and its proof are bounded to SOL-015.

## Remediation summary

Blockers received: 2

Blockers fixed: 0

Blockers remaining: 2

Verification conflicts: 0

Escalations: 1

New follow-up candidates: 0

ESCALATION REQUIRED
