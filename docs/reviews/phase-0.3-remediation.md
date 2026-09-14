# Phase 0.3 blocker remediation handoff

Remediated the four blockers from the initial independent review at commit
`51d06e2`, with generated qualification evidence added afterward. No follow-up
or observation was implemented.

## SOL-014 — Bulk structural key errors are masked by policy errors

Status: **FIXED**  
Related AC: AC-009

Root cause: `update` and `reset` applied per-key freeze/policy checks before
checking all staged names for string validity.

Production changes: `_core.py` now validates the complete staged key collection
for string names before policy checks in both methods.

Before-fix verification: `test_sol014_non_string_bulk_names_precede_frozen_policy`
failed in both update/reset cases with `frozen_instance`.

After-fix verification: the same two protected cases pass with the required
prefixed `TypeError`; state remains unchanged and a later valid write recovers.

Related regression tests: Phase 0.2 mutation/error/rollback suite and scalar
contract tests pass. Sol’s two-case artifact is retained as the regression
contract.

Resolution: structural validation now has batch-wide precedence without changing
atomic staging, freeze policy or missing/read semantics.

## SOL-015 — Mandatory scalar qualification and evidence are missing

Status: **FIXED**  
Related AC: AC-025/026/028

Root cause: the initial implementation had no scalar state-machine oracle and no
post-execution Phase 0.3 evidence writer.

Production changes: `tests/test_stateful.py` adds `ScalarTransactions` with an
independent values/key-order/fields-set oracle and deterministic 100-example by
100-step profile. `tools/qualify_package.py` records source commit,
interpreter/platform, commands, resolved dependencies and artifact hashes, and
writes fresh `docs/research/phase-0.3-findings.md` and
`phase-0.3-results.json` after qualification completes.

Before-fix verification: both SOL-015 cases failed because phase-specific
records did not exist.

After-fix verification: scalar profile passes (2 stateful tests, including the
100 by 100 profile); both SOL-015 cases pass against generated records containing
28 commands, direct/rebuilt hashes and exact source commit.

Related regression tests: existing nested `Transactions` profile and all prior
tests remain retained and pass.

Resolution: required scalar property coverage and honest post-run evidence are
now executable and durable; historical Phase 0.2 records remain untouched.

## SOL-016 — Installed scalar journey does not execute the actual example

Status: **FIXED**  
Related AC: AC-024/028

Root cause: qualification used an unconstrained inline `Config` instead of the
public library-config example and did not assert its complete mapping journey.

Production changes: `examples/library_config.py` now demonstrates typed
Mapping/MutableMapping readers/writers, coupled success/failure with rollback,
metadata, reset and independent copy behavior. `tools/qualify_package.py` copies
and executes this exact source outside the checkout in each bare wheel venv with
`PYTHONPATH` removed.

Before-fix verification: SOL-016 failed because no bare command executed the
example source.

After-fix verification: the protected orchestration case passes; generated
results contain `direct_library_example` and `rebuilt_library_example` records.
The real clean qualification completed successfully for both paths.

Related regression tests: retained bare nested, HTTP, typing, negative-diagnostic
and public-completeness consumers pass.

Resolution: the documented scalar migration path now exercises the actual public
example for both wheel forms.

## SOL-017 — Public strict validation loses scalar entry-mode semantics

Status: **FIXED**  
Related AC: AC-001/020

Root cause: the custom wrap validator’s `next_validator` is Python-mode even when
the public entry point is JSON or strings mode; strict scalar coercion diverged
from pinned Pydantic.

Production changes: `_compat.py` revalidates the unwrapped schema in its original
JSON/strings mode before ownership installation and preserves explicit alias flags
through a context-local entry-options boundary. `_core.py` scopes those options
around public entry calls.

Before-fix verification: SOL-017 failed for strict strings integer and strict JSON
date controls (`int_type`/`date_type`).

After-fix verification: both protected controls pass; explicit alias-flag JSON
and strings tests pass; strict Python rejection remains intact.

Related regression tests: inventory alias/mode, construction/framework,
compatibility remediation, typing and prior suites pass.

Resolution: mode-specific scalar behavior now matches Pydantic 2.13.4 while
retaining detached input, context forwarding, canonical ownership and nested
guards.

## Follow-ups

Existing SOL-011 remains FOLLOW-UP under open GitHub issue #2. No new follow-up
candidates were implemented or created.

## Quality gates

| Gate | Executed | Result | Notes |
| --- | --- | --- | --- |
| Protected blocker suite | Yes | PASS | 7/7 passed. |
| Full tests with plugin autoload disabled | Yes | PASS | Existing suite plus scalar profile completed; globally installed pytest_cases autoload remains an unrelated environment incompatibility. |
| Ruff lint/format and diff check | Yes | PASS | Required files clean. |
| Strict positive/negative typing and verifytypes | Yes | PASS | Exact diagnostics retained; completeness 100%. |
| Documentation checker | Yes | PASS | 39 Markdown files, 255 links, 8 examples. |
| Direct/sdist-rebuilt artifact qualification | Yes | PASS | Both wheels, actual example, HTTP/type consumers and installed completeness. |
| CI candidate matrix | Yes | PASS | Run 34880747496 at `07d3953c8bc5b3be969e452378498ce30597148b`: 8 compatibility lanes, 2 artifact lanes and docs succeeded; package preflight skipped on push. |

## Remediation summary

Blockers received: 4  
Blockers fixed: 4  
Blockers remaining: 0  
Verification conflicts: 0  
Escalations: 0  
New follow-up candidates: 0

READY FOR SOL RE-REVIEW
