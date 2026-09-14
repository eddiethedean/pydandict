# Phase 0.3 — Initial independent production review

Reviewed 2026-09-14 against the [approved contract](../phase-0.3-plan.md).
Candidate: `0d1f2318682d3f52e54d44d7c8f1f1e8d861954e` on `main`.
The candidate was clean at review entry. Only this report and
[blocker verification](../../tests/test_sol_phase03_blockers.py) were added;
production implementation, dependencies and CI configuration were not modified.
No release, push or approval was performed by this review.

The initial implementation corrects non-string `pop` fallback handling and adds
four scalar tests, a source example and an isolated scalar consumer. It does not
complete the qualification contract. Green existing CI is genuine, but does not
prove requirements omitted from the executable gates.

## Acceptance criteria

IDs below mean **0.3/AC**, not similarly numbered historical Phase 0.2 criteria.
VERIFIED rows use inspected existing tests, independently rerun gates and public
API probes. These observations do not substitute for the missing implementation
qualification record under AC-025/026.

| AC | Status | Evidence / outstanding requirement |
| --- | --- | --- |
| AC-001 | NOT SATISFIED | SOL-017: strict JSON date and strings integer diverge from pinned BaseModel; broader scalar controls also reproduce the mode loss. |
| AC-002 | VERIFIED | Phase 0.2 closed-envelope/hash/annotation tests and prototype unsafe-input/output tests; nested consumers remain guarded. |
| AC-003 | VERIFIED | Prototype identity/namespace tests, new scalar reads; public scalar probe includes excluded default field, ABC identity and ordered extras. |
| AC-004 | VERIFIED | Public scalar probe: non-string/missing reads, get, membership, empty record, live views, dict/unpack and mapping pattern; serializers remain separate. |
| AC-005 | VERIFIED | Public scalar key iterator probe: pre-first-next structural invalidation, value-only/failure/no-op stability and persistent exhaustion; inherited iterator tests pass. |
| AC-006 | VERIFIED | Inventory alias/property cases, protected-name paths and explicit alias flag tests; canonical mapping addresses preserved. |
| AC-007 | VERIFIED | Prototype Bounds rollback and Phase 0.3 bulk/metadata tests; cache failure/success probes and prepared-state restoration suite. |
| AC-008 | VERIFIED | Prototype duplicate-pair/keyword precedence and coupled updates; scalar update/union probes; one transaction engine retained. |
| AC-009 | NOT SATISFIED | Pop correction passes, late generator recovery passes; SOL-014 disproves required bulk non-string-before-policy precedence. |
| AC-010 | VERIFIED | Existing-key unused-default tests and scalar typed-extra probe across allow/ignore/forbid policies. |
| AC-011 | VERIFIED | Prototype destructive inventory; public scalar fieldless validator-rejected clear preserves values/order/metadata and recovers. |
| AC-012 | VERIFIED | Inventory data-dependent reset and factory-failure recovery; scalar reversed selection/deduplication probe evaluates defaults in field order. |
| AC-013 | VERIFIED | Public frozen scalar probe covers item/attribute/update/union/setdefault/delete/pop/popitem/clear/reset rejection, equal writes, missing errors and empty/existing no-ops; prior ancestor tests retained. |
| AC-014 | VERIFIED | Snapshot-edit tests, Bounds and Phase 0.3 fields-set/exclude-unset transitions; scalar reset/removal probes. |
| AC-015 | VERIFIED | Prototype canonical drift/programming-exception controls and protected context differential; copy preserves untouched fields. |
| AC-016 | VERIFIED | Full pre-commit and every prepared swap before/after BaseException recovery tests; protected staging reentry and public source-detachment tests pass. |
| AC-017 | VERIFIED | Inventory computed cache tests, protected finalizer lifecycle and public scalar failed/empty/successful cache probe. |
| AC-018 | VERIFIED | Parametrized copy ownership tests, scalar copy test and all public copy/frozen-source/update probes; invalid update/drift controls pass. |
| AC-019 | VERIFIED | Prototype trusted-path tests and scalar deprecated-copy warning/include rejection/construct/deprecated construct/pickle probes; inherited APIs inspected. |
| AC-020 | PARTIALLY SATISFIED | Context, source detachment and alias/extra controls pass; SOL-017 breaks applicable strict entry-mode flags. |
| AC-021 | VERIFIED | Prototype serializer/context/model-serializer controls; scalar exclusion/mapping probe and alias/schema tests; no private-state leaks observed. |
| AC-022 | VERIFIED | Scalar model-vs-dict equality, mutable unhashability and frozen allowed-extra hashing differential against pinned BaseModel pass. |
| AC-023 | VERIFIED | Strict positive/negative helper passes; source completeness and both fresh installed wheel completeness checks pass. |
| AC-024 | PARTIALLY SATISFIED | Both wheel paths genuinely install/run bare and HTTP consumers; SOL-016: complete installed scalar journey and explicit name/version/license/runtime-requirement assertions absent. |
| AC-025 | PARTIALLY SATISFIED | Exact candidate's eight runtime lanes, two artifact lanes and docs pass; SOL-015: fresh AC-linked source/runtime/dependency/command/artifact evidence absent. |
| AC-026 | NOT SATISFIED | SOL-015: no scalar 100 × 100 transition oracle for values, key order and metadata. Existing nested state machine is not this profile. |
| AC-027 | VERIFIED | All 155 candidate tests pass, including previous Sol remediation controls and nested state machine; nested artifact/HTTP consumers pass. |
| AC-028 | PARTIALLY SATISFIED | Source example and existing docs checks pass; SOL-016: actual example not qualified against installed wheels and journey assertions incomplete; SOL-015: evidence reconciliation unfinished. |

## Previous blockers

This is the first Phase 0.3 production review: no previous Phase 0.3 blocker
handoff exists. The [sixth Phase 0.2 review](phase-0.2-rereview-6.md) closed the
historical blockers. Their verification remains required compatibility coverage.

| Finding | Status | Verification / inspected retained fix |
| --- | --- | --- |
| SOL-001 | VERIFIED FIXED | Deferred/resolved annotation, alias/generic and nested ABC completion controls pass; core/adapter audit retained. |
| SOL-002 | VERIFIED FIXED | Model hash-position ingress controls pass; recursive clone/key checks retained. |
| SOL-003 | VERIFIED FIXED | Owned identity/ancestor freeze controls pass; identity writeback path retained. |
| SOL-004 | VERIFIED FIXED | Adapter shape/rebuild/boundary controls pass; version-sensitive operations remain adapter-owned. |
| SOL-005 | VERIFIED FIXED | Source inventory and exact independent negative typing controls pass; helper executed successfully. |
| SOL-006 | VERIFIED FIXED | Both clean artifact paths and exact current CI independently verified; no rebuilt-wheel bypass. |
| SOL-007 | VERIFIED FIXED | Protected benchmark generator/source-baseline contract passes in full suite; historical protocol preserved. |
| SOL-008 | VERIFIED FIXED | Historical Phase 0.2 provenance/readable-summary controls pass. The changed evidence test now checks historical source against its recorded Git commit; this is not fresh Phase 0.3 qualification. |
| SOL-009 | VERIFIED FIXED | Guarded finalizer/disposal and complete swap recovery controls pass; prepared commit retained. |
| SOL-010 | VERIFIED FIXED | Same-root input callback controls pass; staging remains inside guarded transaction. |
| SOL-012 | VERIFIED FIXED | Public existing-model context differential passes; entry forwarding and canonical context separation retained. |
| SOL-013 | VERIFIED FIXED | Existing-model success/failure ownership/strict/source-metadata controls pass; detached-input path retained. |

SOL-015 is a new phase-specific omitted qualification deliverable, not a claim
that the closed historical SOL-008 measurements have become incorrect.

## New blockers

### SOL-014 — Bulk structural key errors are masked by policy errors

Severity: **Medium**. Disposition: **BLOCKER**. Related AC: **AC-009**.

Location: `_core.py` `_check_write`, `update` and `reset` (lines 927, 1094, 1172).

Problem: after staging names, each loop applies both structural and policy
checks to one name before inspecting the next. A frozen first field masks a
later non-string name. The public pop fix addresses only the individual pop case.

Evidence: `update({'fixed': 2, 1: 3})` and `reset('fixed', 1)` both raise
`ValidationError` with `frozen_instance`, not the required prefixed `TypeError`.
Independent probes confirm state is unchanged; the defect is error precedence,
not an observed partial commit.

Relationship to current change: pre-existing scalar interaction explicitly
covered by the approved Phase 0.3 correction/qualification boundary. Not a new
regression attributable to the six-line pop change.

Why it matters / why this blocks: AC-009 explicitly requires non-string mutating
names to fail before policy/validation. Callers must not get a different error
class solely because another staged name is frozen or forbidden.

Required behavior / acceptance criteria: inspect all staged mutating names for
string validity before applying write policy; preserve staging exception
distinctions, rollback and guard recovery. Do not replace atomic batches with
sequential writes or relax freeze semantics.

Verification artifact: `test_sol014_non_string_bulk_names_precede_frozen_policy`
in the linked blocker test file, two cases. Verification status: **CONFIRMED
EXPECTED FAILURE**, each fails at frozen policy rather than the required error.

### SOL-015 — Mandatory scalar qualification and evidence are missing

Severity: **Medium**. Disposition: **BLOCKER**. Related AC: **AC-025/026/028**;
approved P1/P5/P6 qualification work.

Location: `tests/test_stateful.py`, `tests/test_phase03_contract.py`,
`docs/research/` and the implementation completion record.

Problem: the candidate adds four focused scalar examples, but no scalar state
machine or fresh readable/machine-readable AC-linked qualification records.
The existing `Transactions` machine has list/dict/set fields, nested operations,
and a dump/value oracle. Its invariant does not compare root key order or an
independent explicit-fields metadata model. Setting its existing profile to
100 examples/100 steps does not satisfy the distinct scalar transition contract.

Evidence: repository inventory contains only historical Phase 0.2 research
results. `phase-0.3-findings.md` and phase-specific JSON records are absent.
The new scalar file has four deterministic tests; the only existing state
machine remains the nested `Transactions` fixture described above.

Relationship to current change: initial implementation omitted required
qualification; historical results were not overwritten. CI runs the tests that
exist, so a passing CI conclusion cannot establish the missing oracle.

Why it matters / why this blocks: AC-026 explicitly requires at least 100 scalar
sequences of 100 steps with independent values/order/metadata checks and rejection
preservation. AC-025 additionally requires exact reproducible candidate evidence.
These are part of this change's contract, not optional repository improvements.

Required behavior / acceptance criteria: implement and execute the scalar
release profile, retaining the nested machine; record settings/replay information
and comparison of successful and rejected transitions. Publish honest AC-to-test/
lane evidence with exact source identity, actual interpreter/upstream resolutions,
commands, artifact hashes, failures and limitations after the runs. Inventory
applicable scalar matrix cells and reconcile affected milestone claims. Do not
fabricate results, repurpose historical records or assert all-platform proof from
one local run. No numeric beta benchmark ceiling is added by this finding.

Verification artifact: `test_sol015_phase03_has_fresh_qualification_records`,
two cases. Verification status: **CONFIRMED EXPECTED FAILURE**, missing readable
and machine-readable records. These are minimum presence/parseability contracts:
creating empty records is not remediation. Scalar oracle execution and evidence
content require independent re-review; their absence was verified by source
inspection, not by claiming the file-presence test proves the profile.

### SOL-016 — Installed scalar journey does not execute the actual example

Severity: **Medium**. Disposition: **BLOCKER**. Related AC: **AC-024/028**, P5.

Location: `tools/qualify_package.py` bare consumer (lines 109–148),
`examples/library_config.py` (lines 21–34).

Problem: both bare wheels run an inline scalar class without the cross-field
validator in the actual example. It accepts every low/high pair, so its successful
update cannot prove coupled atomic rejection. The actual example is not invoked
by the driver. It also lacks the required mapping-only reader/writer, copy and
explicit metadata journey assertions. Twine/marker checks are present, but
explicit installed name/version/license/runtime-requirement policy assertions
are absent.

Evidence: independently executed qualification succeeded for both wheel paths;
its recorded commands contain only the unconstrained inline `Config` and
HTTP/type consumers, never the actual library-config example. The source example
executes successfully on `PYTHONPATH=src`, which is not an installed-wheel proof.

Relationship to current change: incomplete newly introduced scalar artifact
consumer; retained nested bare and HTTP checks continue passing.

Why it matters / why this blocks: the approved journey must demonstrate the
public scalar model as a replacement in library-facing mapping code, including
coupled success/failure, reset, metadata and valid independent copies, against
both wheel paths without development dependencies or source injection.

Required behavior / acceptance criteria: complete the public example assertions
and actually run that example outside the checkout in each bare wheel environment
with `PYTHONPATH` cleared. Retain guarded nested/HTTP/type checks and assert the
installed distribution's promised metadata and dependency policy. Record actual
execution and outcomes; do not merely insert a path into a report.

Verification artifact:
`test_sol016_qualification_executes_actual_example_against_both_bare_wheels`.
Verification status: **CONFIRMED EXPECTED FAILURE**, no bare artifact path runs
the actual example. This mocked orchestration contract accepts file/inline/
referenced-wrapper execution; real clean-environment example assertions and
metadata checks must also pass at re-review. It is not a substitute for real
integration execution.

### SOL-017 — Public strict validation loses scalar entry-mode semantics

Severity: **High**. Disposition: **BLOCKER**. Related AC: **AC-001/020**.

Location: `_compat.py` `wrap_model_schema` (lines 313–345), `_core.py`
schema finish/input detachment and `model_validate_json`/`model_validate_strings`.

Problem: the wrapper detaches entry input before forwarding it to the inner
validator. The resulting strict validation treats scalar strings as Python values
rather than preserving the original JSON/strings acceptance semantics. Public
methods forward `strict`, but that alone does not preserve mode compatibility.

Evidence using Pydantic 2.13.4 controls:

- `BaseModel.model_validate_strings({'value': '2'}, strict=True)` yields integer
  `2`; equivalent DictModel raises `int_type`.
- `BaseModel.model_validate_json('{"value":"2026-01-01"}', strict=True)` yields
  `date(2026, 1, 1)`; equivalent DictModel raises `date_type`.
- Additional independent controls reproduce strings-mode failures for bool,
  float, bytes, Decimal, date, naive datetime, naive time and timedelta; strict
  JSON bytes/Decimal/date/naive datetime/time/timedelta similarly fail.

Relationship to current change: retained pre-existing entry-wrapper defect, not
introduced by pop remediation, but explicitly in scope for scalar strictness/
mode qualification. Existing construction tests mostly use non-strict modes.

Why it matters / why this blocks: supported scalar construction with applicable
flags must match the pinned schema's mode-specific acceptance. Valid strict
application inputs are rejected, violating AC-001/020 and required compatibility.

Required behavior / acceptance criteria: preserve applicable Python/JSON/strings
semantics through safe source detachment and installation. Keep strict Python
rejection, input isolation, context forwarding, canonical drift and prior nested
ownership guarantees; do not solve this by globally disabling strictness.

Verification artifact: `test_sol017_strict_scalar_entry_modes_match_pinned_basemodel`,
two representative cases plus a strict-Python negative control. Verification
status: **CONFIRMED EXPECTED FAILURE**, `int_type` and `date_type` respectively.

## Quality gates and provenance

Local reviewer runtime: macOS 26.5.2/arm64, CPython 3.11.14,
Pydantic 2.13.4 / pydantic-core 2.46.4. Source checks explicitly resolve `src`;
the pre-existing local installed metadata mismatch is not artifact evidence.

| Gate actually executed | Result | Classification |
| --- | --- | --- |
| Candidate full suite: `PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests -q` | 155 passed in 102.95s before review tests | PASS |
| Blocker-only suite, same environment, `tests/test_sol_phase03_blockers.py -q --tb=short` | 7 failed in 0.37s, all matching documented reasons | EXPECTED BLOCKER VERIFICATION |
| Full suite including review verification: same environment, `python -m pytest tests -q --tb=no --show-capture=no` | 155 passed, 7 failed in 102.75s; only the seven new blocker cases fail | EXPECTED BLOCKER VERIFICATION |
| Ruff check and format check on required source/tests/helpers; review test separately checked | Pass; candidate 25 files formatted | PASS |
| `python tools/check_typing.py` | Strict positive and exact negative checks pass | PASS |
| `PYTHONPATH=src python -m pyright --verifytypes pydandict --ignoreexternal` | Public completeness 100%; no errors | PASS |
| `python tools/check_docs.py` before report | 38 Markdown files, 252 links, 8 Python examples; zero errors | PASS |
| Final docs, Ruff/format and `git diff --check` including review artifacts | 39 Markdown files, 255 links, 8 examples; zero errors; 26 Python files formatted | PASS |
| `PYTHONPATH=src python examples/library_config.py` | Pass | PASS for source only |
| `python tools/qualify_package.py` | Both fresh direct and sdist-rebuilt wheel consumers, HTTP, installed positive/negative typing and completeness pass | PASS for implemented checks; SOL-016 remains |
| Public scalar mapping/iterator/generic/hash probe | Pass | PASS |
| Public frozen/no-op/extra/reset/clear/cache/copy/trusted-path probe | Pass | PASS |
| Strict entry-mode BaseModel differentials | Required acceptance mismatch | IN-SCOPE BLOCKER; pre-existing implementation |
| Initial unrestricted pytest plugin autoload | Fails before collection inside globally installed pytest_cases, incompatible IdMaker signature | ENVIRONMENT / UNRELATED; prescribed plugin-disabled run passes |

Fresh reviewer artifact hashes (observations, not a completed Phase 0.3 release
profile): sdist `af71d769cb9c066b6b788c4b22f83db267c21d0eaec28e2cd6c198cf8fb5bb97`;
direct wheel `5f7e2b7a586ce87a593ffc8276b6937294e2cf343cb61bce612f4be035d54901`;
rebuilt wheel `f9f571cacb1a67aba10a5bdb8d87bbbef9253acd6041fc887e113bdcda014be6`.
Both wheels are `pydandict-0.2.0-py3-none-any.whl`. Bare resolutions contain
Pydantic 2.13.4, core 2.46.4, annotated-types 0.8.0,
typing-inspection 0.4.4 and typing_extensions 4.16.0; no development tools.
HTTP resolutions include FastAPI 0.141.1, httpx 0.28.1, Pyright 1.1.411 and
Starlette 1.6.0. These are local resolved stacks, not every CI lane's stack.

Independently queried [CI run 34876678232](https://github.com/eddiethedean/pydandict/actions/runs/34876678232):
completed success at the exact candidate SHA. Eight advertised OS/Python
compatibility lanes, Ubuntu 3.11/3.14 artifact lanes and docs succeeded.
Release-only package preflight was skipped on the push as expected. The run
predates the intentional review tests and does not include missing scalar gates.
No new scalar performance profile or publication was performed by this review;
no performance ceiling is made a blocker.

## Follow-ups and observations

Open GitHub issues were searched again; no new unrelated follow-up was confirmed.

| Finding | Severity | Disposition / GitHub status |
| --- | --- | --- |
| SOL-011 — Repeated recursive-root after-validator invocation | Low | FOLLOW-UP; EXISTING ISSUE [#2](https://github.com/eddiethedean/pydandict/issues/2), verified open; retained historical disposition, outside this scalar change. |

Observation: issue #1 status reconciliation and untouched historical planning
vocabulary remain separate maintainer work. Neither is assigned a current blocker
or new issue. No async, persistence, new timezone types, broader dependency
support, performance optimization or repository-wide cleanup is requested.

## Convergence and handoff

Historical blockers remain closed; previous Phase 0.3 blockers resolved: not
applicable (first review). **Four blockers remain: SOL-014/015/016/017.**
New blockers attributable to remediation: **0**. Two are pre-existing behavior
violations explicitly in scope; two are initial qualification omissions. New
unrelated follow-ups: **0**. No repeated-failure escalation is warranted yet.

The boundary is fixed and remediation is bounded: preserve all previous tests,
correct the two demonstrated behavior contracts, complete scalar qualification
and the real installed journey, then refresh exact-candidate evidence. Only the
four blockers go to implementation; do not fold SOL-011 or observations into it.

NEEDS FIXES
