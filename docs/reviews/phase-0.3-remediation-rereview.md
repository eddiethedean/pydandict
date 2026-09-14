# Phase 0.3 re-review blocker remediation

This remediation addresses only SOL-015, SOL-016 and SOL-017 from the latest
[independent re-review](phase-0.3-rereview.md). Sol's review report and its
verification artifacts remain unchanged.

## SOL-015 — Qualification evidence is incomplete and not protected from invalid runs

Status: **FIXED**

Related AC: AC-025/028

Root cause: `tools/qualify_package.py` unconditionally replaced durable evidence
after any successful orchestration, including mocked runs that had no Git source
identity. Its record lacked an explicit complete AC-to-test/lane boundary and the
scalar profile/replay settings.

Production changes: `tools/qualify_package.py` now validates a 40-character Git
source identity before writing durable records. A missing identity produces a
non-qualifying result and preserves existing evidence. Qualified records include
all AC test/lane mappings, the scalar stateful profile, observed-failure and
limitation fields. The readable companion distinguishes this local artifact gate
from required runtime, docs and all-platform CI gates.

Before-fix verification: Sol's
`test_sol015_missing_provenance_cannot_replace_durable_evidence` failed because a
blank source identity overwrote its isolated durable-record sentinel.

After-fix verification: the same protected test passes. Mocked orchestration
retains a non-qualifying status without writing evidence; a fresh real direct and
sdist-rebuilt qualification wrote source identity
`b8ff5071d215baca6c44a109ba6d0ebbae627ded`, command/resolution records and
artifact hashes.

Related regression tests: complete `tests/` runtime suite; post-commit benchmark
provenance run.

Additional tests: none; the Sol contract exercises isolated evidence preservation
without relying on an implementation-specific output schema.

Resolution: valid real runs create explicit, truthful evidence; incomplete/mock
runs cannot replace it. The record makes its limits visible rather than claiming
that one local artifact run proves the full CI matrix.

## SOL-016 — Installed metadata/dependency policy remains unverified

Status: **FIXED**

Related AC: AC-024/028

Root cause: qualification ran the actual scalar example but never inspected the
installed distribution metadata or its packaged license and runtime requirements.

Production changes: each bare wheel environment now verifies installed metadata
through `importlib.metadata`: name `pydandict`, version `0.2.0`, SPDX
`License-Expression: MIT`, exactly the runtime direct requirement
`pydantic==2.13.4`, and the installed MIT license file. Existing py.typed,
mapping example, nested, HTTP, typing and negative-diagnostic consumers remain.

Before-fix verification: Sol's protected orchestration test passed only the
actual-example requirement; source inspection confirmed no installed metadata
consumer existed.

After-fix verification: fresh direct and sdist-rebuilt wheel qualification passes
both metadata consumers (`direct_metadata` and `rebuilt_metadata` each record
`metadata verified`) with no source-path injection.

Related regression tests: protected SOL-016 orchestration contract, full runtime
suite and both real artifact consumer paths.

Additional tests: none; real clean-wheel execution verifies the installed
distribution rather than a source-metadata proxy.

Resolution: both artifact forms now prove the required installed metadata,
license material and direct-runtime dependency policy while retaining the complete
public scalar journey.

## SOL-017 — Mode replay loses entry options and runs callbacks before detachment

Status: **FIXED**

Related AC: AC-001/020

Root cause: the first replay fix eagerly parsed JSON/strings before the core
transaction detached input and did not carry strict, extra or context overrides
into its replacement SchemaValidator.

Production changes: public `DictModel` entry methods pass alias/name, strict,
extra and context through a scoped adapter entry boundary. `_compat.wrap_model_schema`
now invokes JSON/strings parsing only from the callback supplied to `finish`; the
existing transaction therefore clones input before user validators execute. The
replayed SchemaValidator receives every applicable entry override.

Before-fix verification: Sol's three
`test_sol017_json_entry_options_match_pinned_basemodel` cases failed for strict,
extra and context; `test_sol017_rejected_strings_callback_cannot_mutate_entry_source`
showed a rejected callback editing caller input.

After-fix verification: all four cases pass, as do the two original strict
strings/JSON controls and strict-Python negative control.

Related regression tests: explicit public alias flags in Python/JSON/strings,
compatibility remediation, transaction remediation and full runtime suite.

Additional tests: none; Sol's five distinct entry-contract cases already cover
the affected option propagation and source-isolation invariants.

Resolution: JSON and strings retain Pydantic mode behavior while strictness,
extra policy, context, aliases and callback input isolation remain consistent
with the public entry contract.

## Follow-up report

Existing Sol FOLLOW-UP: SOL-011 (recursive root after-validator invocation,
GitHub issue #2) was not changed.

New follow-up candidates: none.

## Quality gates

| Gate | Executed | Result | Notes |
| --- | --- | --- | --- |
| Sol Phase 0.3 blocker contracts | Yes | PASS | 12 passed in 0.16s. |
| Full runtime suite | Yes | PASS | 168 passed in 103.05s after the remediation commit. |
| Post-commit benchmark provenance | Yes | PASS | Three baseline/candidate complete runs; current-source hash assertion passes. |
| Ruff required inventory and formatting | Yes | PASS | Required files clean. |
| Strict positive/negative typing | Yes | PASS | Exact expected diagnostics retained. |
| Installed public completeness | Yes | PASS | 100%, no errors. |
| Documentation checker | Yes | PASS | 43 Markdown files, 260 links and 8 Python examples after final evidence/report update. |
| Direct/sdist-rebuilt qualification | Yes | PASS | Actual scalar example, metadata policy, nested/HTTP/type consumers and installed checks pass. |

## Remediation summary

Blockers received: 3

Blockers fixed: 3

Blockers remaining: 0

Verification conflicts: 0

Escalations: 0

New follow-up candidates: 0

READY FOR SOL RE-REVIEW
