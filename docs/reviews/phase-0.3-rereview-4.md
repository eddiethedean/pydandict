# Phase 0.3 — Fourth independent production re-review

Reviewed 2026-09-14 against the [approved contract](../phase-0.3-plan.md),
the retained Phase 0.2 closed-input/integration contract, the
[third review](phase-0.3-rereview-3.md), the
[implementation handoff](phase-0.3-remediation-final.md) and its
[executed evidence reconciliation](../research/phase-0.3-final-execution.json).
Candidate: `3de7d66bf875dc50d52ebe13132fdc0be6a72f30`, clean at entry.
Production remediation: `d0e80850be769be2c85e7b1d1230b76cbeefcdc4`.
Only this report and [blocker verification](../../tests/test_sol_phase03_rereview_4.py)
were added to the current checkout. Production, previous tests, workflows,
dependencies and committed qualification records are unchanged. No commit,
push or publication was performed.

SOL-015 is VERIFIED FIXED. SOL-017 is PARTIALLY FIXED: all its previous
native-mode regressions now pass, but the replacement schema boundary removes
the Python input guard when embedded in supported framework envelopes.
This introduced regression violates the existing closed-input contract; it is
not a request to support a new nested type or make the repository globally perfect.

## Acceptance criteria

Verification combines contract/fix inspection, the independently rerun entire
562-case candidate suite, focused controls, evidence content audit and actual
exact-HEAD CI. A green suite alone does not establish the newly exposed invariant.

| AC | Status | Evidence / outstanding requirement |
| --- | --- | --- |
| AC-001 | VERIFIED | Native leaf/annotation/strictness differentials and every protected native-mode regression pass. |
| AC-002 | REGRESSED | Embedded scalar subclasses and arbitrary attribute inputs escape rejection, SOL-017. Standalone rejection and final-output guards still pass. |
| AC-003 | VERIFIED | ABC identity, canonical/default/excluded keys, extra order and direct mapping consumers pass. |
| AC-004 | VERIFIED | Reads/membership/get/live views/unpacking/patterns bypass serializers; empty/missing consumers are evidenced. |
| AC-005 | VERIFIED | Direct iterator creation, before/after-first-next invalidation, value/failure/no-op stability and permanent exhaustion assertions pass. |
| AC-006 | VERIFIED | Namespace/alias controls and alias-only/name-only native option differentials pass. |
| AC-007 | VERIFIED | Scalar single-write policy, rollback, metadata and cache assertions pass. |
| AC-008 | VERIFIED | Batch/duplicate/keyword/in-place union/self-update assertions and scalar oracle pass. |
| AC-009 | VERIFIED | Protected SOL-014 precedence, malformed pairs and late iterable failure/recovery pass. |
| AC-010 | VERIFIED | Existing/missing setdefault, unused fallback, typed-extra coercion and ignore/forbid rejection pass. |
| AC-011 | VERIFIED | Declared-removal protection, last-key/empty/missing behavior and fieldless rejected-clear rollback pass. |
| AC-012 | VERIFIED | Selected factory order/once-only/deduplication, reset metadata and exception recovery pass. |
| AC-013 | VERIFIED | Required/defaulted/nullable × policy × freeze controls cover equal/mixed writes and specified no-ops. |
| AC-014 | VERIFIED | Detached metadata snapshots, explicit/reset/extra transitions and exclude-unset assertions pass. |
| AC-015 | VERIFIED | Canonical Python/context=None, drift and programming-exception controls pass; transaction engine is retained. |
| AC-016 | VERIFIED | Staging/callback reentry, prepared-swap/BaseException recovery and native callback/factory isolation controls pass. |
| AC-017 | VERIFIED | Direct scalar and retained cache success/failure/no-op identity controls pass. |
| AC-018 | VERIFIED | Same-type independent shallow/deep/frozen validated copies, metadata, invalid updates and drift controls pass. |
| AC-019 | VERIFIED | Deprecated/inherited copy/parse/dump/schema and disabled construct/pickle inventory passes. |
| AC-020 | REGRESSED | Native mode/options/context and standalone existing-model controls pass; embedded Python ingress bypasses the required closed-input boundary, SOL-017. |
| AC-021 | VERIFIED | Scalar dump/JSON/schema aliases, exclusion/filter/context/custom serializer controls pass; no engine metadata leaks. |
| AC-022 | VERIFIED | Direct model-versus-dict equality, extra differences, mutable unhashability and frozen BaseModel hash parity pass. |
| AC-023 | VERIFIED | Strict positive/exact four negative diagnostics and public completeness 100%; actual clean-wheel static gates pass. |
| AC-024 | VERIFIED | Direct/rebuilt installed example, metadata/MIT/dependency/py.typed and nested/HTTP consumers pass locally and in both artifact CI lanes. |
| AC-025 | VERIFIED | All 11 advertised applicable HEAD jobs pass; actual source-qualified versions/commands/hashes and reconciled AC cells are present. |
| AC-026 | VERIFIED | Both independent scalar and retained nested machines execute 100 examples × 100 steps, deadline=None, derandomize=True. |
| AC-027 | REGRESSED | All retained tests pass, but inherited closed Python ingress is lost in ordinary BaseModel/collection envelopes, SOL-017. No supported annotation or collection mutator was removed. |
| AC-028 | PARTIALLY SATISFIED | Actual installed example/docs/evidence inventory pass. The documented closed arbitrary-object/subclass boundary does not match embedded behavior, SOL-017. |

## Previous blockers

| Finding | Status | Verification / root-cause inspection |
| --- | --- | --- |
| SOL-014 | VERIFIED FIXED | Protected bulk non-string update/reset precedence passes; staging implementation retained. |
| SOL-015 | VERIFIED FIXED | Complete content audit, real node/cell reconciliation, direct iterator/hash anchors, protected invalid-provenance controls and fresh qualification pass. |
| SOL-016 | VERIFIED FIXED | Both actual wheel paths execute the scalar example and installed metadata assertions. |
| SOL-017 | PARTIALLY FIXED | All previous Phase 0.3 entry regressions pass; four new embedded-ingress controls fail as expected. Native modes are repaired, but required ingress rejection regresses. |
| SOL-001 | VERIFIED FIXED | Retained annotation/generic/deferred completion and specialization controls pass. |
| SOL-002 | VERIFIED FIXED | Retained unsafe hash-ingress controls pass. |
| SOL-003 | VERIFIED FIXED | Retained owned identity/ancestor freezing controls pass; reconciliation is unchanged. |
| SOL-004 | VERIFIED FIXED | Adapter shape/deferred rebuild/class-local cache controls pass. |
| SOL-005 | VERIFIED FIXED | Required strict inventory and exact negative diagnostics pass. |
| SOL-006 | VERIFIED FIXED | Actual direct/rebuilt wheel paths and both advertised artifact lanes pass. |
| SOL-007 | VERIFIED FIXED | Retained executable benchmark baseline/generator contracts pass. |
| SOL-008 | VERIFIED FIXED | Historical benchmark provenance controls pass; current-phase evidence is separately closed under SOL-015. |
| SOL-009 | VERIFIED FIXED | Retained finalizer/disposal/prepared-swap/BaseException recovery controls pass. |
| SOL-010 | VERIFIED FIXED | Retained staged-input and callback reentry controls pass. |
| SOL-012 | VERIFIED FIXED | Protected existing-model Python context and public JSON context controls pass. |
| SOL-013 | VERIFIED FIXED | Protected existing-model ownership and public strings source-isolation controls pass. |

### SOL-015 closure audit

All 43 recorded component SHA-256 values match HEAD. The recorded 562 node IDs
exactly match independently collected candidate nodes; every proof node resolves.
All 28 ACs have 11 explicit executed/non-applicable job cells; every passed cell
resolves to an actual successful recorded job. Behavioral axes/exclusions are
separate from job applicability, including null strings, custom tzinfo,
unsupported generic/concrete annotation success, frozen/destructive rejection,
context-free transactions and mutable hash rejection.

The direct AC-005 and AC-022 assertions genuinely prove the previously missing
iterator/hash/equality outcomes. Source-qualified commands, resolved dependencies,
manual consumer checks, stateful settings, actual local/CI artifact hashes,
failures/limitations and preserved historical/non-qualifying records are present.
The measured `7476dec` evidence is explicitly retained rather than falsely
relabeled as HEAD; the subsequent HEAD changes only documentation. Newly
discovered runtime failure is SOL-017, not grounds to reopen this evidence-format
blocker. The next implementation handoff must reconcile its new verification.

## Remaining blocker

### SOL-017 — Native embedding removes the closed Python ingress boundary

Severity: High.
Disposition: BLOCKER.
Related AC: AC-002/020/027/028; the previous AC-001 native-mode symptoms are fixed.

Location: `src/pydandict/_compat.py`, `_native_model_schema` lines 19–24,
`wrap_model_schema` lines 455–460 and 486–500;
`src/pydandict/_core.py`, native completion/output installation.

Problem: embedding replaces the public json-or-python schema with its native
JSON branch and returns that boundary directly. A containing DictModel reconstructs
Python wrappers, but ordinary BaseModel envelopes and TypeAdapter collections do
not. Their Python validation therefore runs without the child input clone/audit.
Detaching validated fields and installing ownership afterwards cannot reject
unsupported inputs that Pydantic has already converted to supported integers.

Evidence: a scalar `Child(DictModel)` with `value: int`, embedded as
`child: Child` in an ordinary BaseModel or as `TypeAdapter(list[Child])`, accepts:

- `{"value": ScalarSubclass(2)}` where ScalarSubclass inherits int;
- `SimpleNamespace(value=2)` with `from_attributes=True`.

Standalone TypeAdapter(Child) rejects both with `pydandict_unsupported_value:`.
Supported ordinary dictionary input containing `"2"` continues to produce a
guarded Child with integer 2 in both embedded routes.

Relationship to current change: the same four automated cases pass against
previous reviewed production `5c72df2`; they fail against HEAD with
`DID NOT RAISE TypeError`. The removal is introduced by remediation `d0e8085`.
Ordinary BaseModel envelopes and TypeAdapter collections are inherited supported
integrations, not ordinary BaseModel values newly allowed inside DictModel fields.
The Phase 0.3 contract explicitly requires arbitrary objects/scalar subclasses to
remain rejected, and Phase 0.2 explicitly excludes arbitrary attribute ingress.

Why it matters: required input policy depends on how the same scalar model is
embedded. Final-output ownership can remain valid while unsupported original
inputs silently bypass the public construction contract.

Why this blocks the current change: this is an introduced compatibility regression
in behavior modified to remediate SOL-017, violating AC-002 and the retained
framework-entry boundary. Blocker tests 1/2/3/5 apply; this is not merely a real
unrelated bug or a request for a wider envelope. Stable SOL-017 is preserved
because native-mode repair still fails its required mode-plus-ingress invariant.

Required behavior: preserve closed Python input rejection in standalone and
embedded supported entry paths while retaining genuine native JSON/strings
strictness/options, aliases/context, source isolation, defaults, discriminators,
recursive references, ownership and canonical Python transactions.

Acceptance criteria: both embedded routes reject the original unsupported scalar
subclass and attribute sources with the supported diagnostic before returning a
model. Supported dictionary coercion still succeeds. Every prior SOL-017 test and
the retained nested/framework suite remains green. No particular implementation,
callback count or framework monkeypatch is prescribed.

Verification artifact:
`tests/test_sol_phase03_rereview_4.py::test_sol017_embedded_python_ingress_rejects_unsupported_sources`.
Verification status: CONFIRMED EXPECTED FAILURE, four cases in 0.15s;
previous-candidate differential: four passed in 0.12s. Standalone rejection and
supported-input controls succeed before each current embedded rejection fails.

ESCALATION RECOMMENDED: SOL-017 survives more than one implementation attempt.
Architectural reconsideration is still indicated: the mode-preserving schema
boundary must also preserve the input policy under embedding. The current native
semantics improvement is real; removing the guard is not a complete resolution.
No specification or external/environment clarification is needed for this failure.

## Quality gates and provenance

| Gate | Result | Classification |
| --- | --- | --- |
| Full candidate suite, collected before new review tests | 562 passed in 105.88s | PASS |
| Protected Phase 0.3 and direct evidence controls | 24 passed in 0.31s | PASS |
| New blocker verification on HEAD production | Four expected failures | EXPECTED BLOCKER VERIFICATION |
| New verification against previous production | Four passed | Confirms change attribution |
| Required Ruff lint/format inventory | Pass, 32 candidate files; new test independently clean | PASS |
| Strict typing helper | Pass, exact positive/negative inventory | PASS |
| Public completeness | 100%, zero errors | PASS |
| Candidate docs | 52 Markdown files, 293 local links, eight examples, zero errors | PASS |
| Fresh external direct/rebuilt qualification | Pass after local interpreter PATH correction | PASS |
| Exact-HEAD CI | Eight runtime, two artifact, one documentation jobs succeed | PASS; predates new review tests |

Final checks including this report and new test: 53 Markdown files, 298 local
links, eight examples, zero errors; lint/format pass with 33 required files;
whitespace check passes. The current worktree contains only these two untracked
review artifacts.

Runtime command: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src python -m pytest -q`.
Focused/new commands use the same environment with the named test files; the
previous differential selects `/Volumes/T7/pydandict-sol-third-cOhhBy/checkout/src`.
Other commands: CI's exact Ruff inventory, `python tools/check_typing.py`,
`PYTHONPATH=src python -m pyright --verifytypes pydandict --ignoreexternal`,
`python tools/check_docs.py`, `git diff --check`.

Fresh qualification runs in the detached exact-HEAD checkout at
`/Volumes/T7/pydandict-sol-fourth-ir2wRX/checkout`, leaving current committed
qualification records untouched. It clears PYTHONPATH and builds/installs outside
the checkout. Its local record retains actual commands, freezes, installed imports,
example/metadata outputs, artifact hashes and source HEAD. Python 3.11.14,
macOS 26.5.2 arm64; Pydantic 2.13.4/core 2.46.4, FastAPI 0.141.1,
HTTPX 0.28.1, Starlette 1.6.0 and Pyright 1.1.411.
The final unmodified-driver run records 31 commands and succeeds with both
metadata checks, both external installed imports and both exact four-diagnostic
negative gates. Command: `python tools/qualify_package.py`, with the Python 3.11
libexec/bin and bin directories first in PATH, external TMPDIR at
`/Volumes/T7/pydandict-sol-fourth-ir2wRX` and the retained external pip cache.

Two initial local artifact attempts failed at isolated Pyright's typing.assert_type
lookup. Putting `/opt/homebrew/opt/python@3.11/libexec/bin` first in PATH resolves
the local interpreter-selection failure without changing source/configuration or
weakening diagnostics. The artifact build/install/static execution section is
unchanged from the previous candidate. This resolved environmental failure is not
excused as an unproven pre-existing production defect. An initial hash-audit shell
variable collided with zsh PATH, and an initial job-reference query assumed an
object rather than an array; corrected audits pass. Neither diagnostic error is
evidence of an implementation mismatch.

[Exact-HEAD CI](https://github.com/eddiethedean/pydandict/actions/runs/34894161787)
is independently confirmed completed/success. Both artifact job logs contain
qualified source HEAD, 31 real commands, installed metadata and exact four
negative diagnostics for direct/rebuilt paths. Their CPython versions are
3.11.16 and 3.14.7. The Ubuntu 3.11 runtime log independently reports 562 passed,
strict checks passed and public completeness 100%. Release-only preflight is
correctly skipped on push. CI does not cover the newly added four review cases.

| Exact-HEAD artifact measurement | Sdist SHA-256 | Direct wheel SHA-256 | Rebuilt wheel SHA-256 |
| --- | --- | --- | --- |
| Local CPython 3.11.14 | `07984e6b0f25257898e8d6486780674536820017fde8db3d4c4156ca252c5f95` | `810792b55122fa9f57b969a5d4e70001f17ac0684775ee65b9a1459c9846f69d` | `9f677beb0d932cb4cbca9fe0b6e6027dbf8235ba5e8d8dc0b3a4f5052ca5b4e6` |
| CPython 3.11.16 | `756189e893d61f6d28a568331d0a35dade7f2f39d05785721d77c973ea3db676` | `1b4c44cb95709ee8d781838b384c5b476ab4d6cf555938463eaa09667e28e52b` | `51e34214002ae277f3f698f9a00447c397773c536ac17b30c9cf6343dadaaca2` |
| CPython 3.14.7 | `1420f7604d764bb85f0e30ede8bbf58b223c9d79a0224e4fc1a8bb01ba9c5ded` | `d41a1d465bb7a48fb65bfb01a8dba8563b644b76f55dbd5e070eb37227bd25d7` | `4a75f704084e1a620ce355ada03c573807aabfb1e39201061fa22184a375074e` |

## Follow-ups and observations

| Finding | Severity | GitHub issue |
| --- | --- | --- |
| SOL-011 — Repeated recursive root after-validator invocation | Low | EXISTING ISSUE [#2](https://github.com/eddiethedean/pydandict/issues/2), confirmed OPEN |

SOL-011 remains FOLLOW-UP, related AC NONE. The issue contains the historical
baseline differential, affected core/benchmark symbols, reproducer and proposed
verification. Deterministic rerunnable callbacks and unchanged transaction
semantics keep it outside this change's blockers; exact recursive callback counts
are not promised. Open issues were searched; no duplicate issue or failing
follow-up test was created. No new unrelated follow-ups were discovered.

Observations: existing upstream deprecation notices, including Pyright's newer
version notice, do not justify widening pinned tooling/dependencies or the review
boundary. No observation is handed to implementation.

## Convergence

Previous blockers newly resolved: one, SOL-015. SOL-014/016 and retained Phase 0.2
blockers remain verified fixed. Blockers remaining: one, SOL-017 PARTIALLY FIXED.
New blockers attributable to remediation: one embedded-ingress regression within
the same stable SOL-017, no new finding ID. Follow-ups discovered: zero new; one
existing nonblocking follow-up retained.

The evidence loop has converged, and native-mode semantics have materially
improved. The overall remediation loop has not yet converged because a required
ingress guarantee was traded away under embedding. Only SOL-017 goes to
implementation; do not ask implementation to fix follow-ups or observations.

NEEDS FIXES
