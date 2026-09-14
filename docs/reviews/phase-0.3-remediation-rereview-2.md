# Phase 0.3 second re-review blocker remediation

This remediation addresses only SOL-015 and SOL-017 from the latest independent
review. Sol's review report and protected verification artifacts are unchanged.

## SOL-017 — Replacement mode validator still loses TypeAdapter entry options

Status: **FIXED**

Related AC: AC-001/020

Root cause: the class-method ContextVar replay restored JSON/strings mode for
`DictModel.model_validate_*`, but `TypeAdapter` enters the core schema directly.
Pydantic's `ValidationInfo` deliberately does not expose dynamic `strict` or
`extra`; rebuilding a replacement validator therefore used configuration rather
than the adapter request.

Production changes: `src/pydandict/_compat.py` now first uses the original
handler for direct TypeAdapter entry, retaining Pydantic's dynamic strict/extra
policy. Only when Python-mode handling rejects a scalar representation that the
native JSON/strings mode accepts (bytes, date/time/duration or Decimal) does it
replay that representation in native strict mode, then return through the
original handler so the dynamic extra policy is applied. Class-method entry keeps
the existing explicit option boundary and source detachment.

Before-fix verification: Sol's
`test_sol017_type_adapter_strict_json_matches_pinned_basemodel` failed because a
strict JSON string integer was accepted by `DictModel`.

After-fix verification: all thirteen protected SOL-014/015/016/017 cases pass.
The Sol TypeAdapter strict contract now rejects identically to BaseModel. Added
implementation coverage compares BaseModel and DictModel strict JSON date input
with each `extra` override (`forbid`, `ignore`, `allow`).

Related regression tests: Phase 0.2 nested identity, strict entry-mode,
class-method option/context/isolation and scalar contracts.

Additional tests: `test_type_adapter_native_mode_keeps_dynamic_strict_and_extra_options`
in `tests/test_compat_remediation.py` covers the native-mode fallback plus dynamic
extra-policy interaction not represented by Sol's integer-only contract.

Resolution: TypeAdapter now retains both its requested strictness/extra policy
and Pydantic's native scalar JSON/string semantics without exposing caller input
to callbacks.

## SOL-015 — Required AC-to-test-node/executed-lane inventory is incomplete

Status: **FIXED**

Related AC: AC-025/028

Root cause: the qualification record generated one generic full-suite label for
AC-001 through AC-023. It did not identify executable proof nodes or distinguish
artifact execution from external runtime/docs lanes.

Production changes: `tools/qualify_package.py` now records an explicit AC-001
through AC-028 test-node inventory. Every map entry identifies concrete test/tool
nodes and lane execution state; the record marks artifact work executed by the
driver while retaining external runtime/docs gates as required external evidence.
The readable findings document renders the same complete inventory. The existing
invalid-provenance protection, settings, failures and limitations remain intact.

Before-fix verification: Sol's manual audit found only generic `tests/ (full
runtime suite)` placeholders, not the P1/P5/P6 inventory requirement.

After-fix verification: a fresh direct/sdist-rebuilt qualification for source
`912b309350d94f75b8a8608f71c83b8d13132e05` produces all 28 AC entries with
specific test nodes and explicit lane state, plus commands, resolutions, hashes,
settings, observed failures and limitations. Sol's invalid-provenance sentinel
test also passes.

Related regression tests: `test_sol015_missing_provenance_cannot_replace_durable_evidence`
and qualification's direct/rebuilt consumer paths.

Additional tests: none; the review requires auditable content, not an
implementation-specific record schema. The fresh result and readable rendering
are inspected directly.

Resolution: durable qualification evidence now ties every approved AC to its
actual executable proof and honestly separates run artifact work from required
external gates.

## Follow-up report

Existing Sol FOLLOW-UP: SOL-011 (recursive root after-validator invocation,
GitHub issue #2) was not changed.

New follow-up candidates: none.

## Quality gates

| Gate | Executed | Result | Notes |
| --- | --- | --- | --- |
| Protected Phase 0.3 contracts | Yes | PASS | 13 passed. |
| Related Phase 0.2 blocker contracts | Yes | PASS | Includes nested identity and benchmark provenance. |
| Benchmark provenance | Yes | PASS | 1 passed in 124.10s after source stabilized. |
| Ruff required inventory/format | Yes | PASS | Clean. |
| Strict positive/negative typing | Yes | PASS | Exact diagnostics retained. |
| Public completeness | Yes | PASS | 100%, no errors. |
| Documentation checker | Yes | PASS | 44 Markdown files, 265 links, 8 examples before this report. |
| Direct/sdist-rebuilt qualification | Yes | PASS | Fresh full artifact consumers and evidence record. |
| Complete suite | Yes | PASS | 170 passed in 121.99s with stable source hashes. |

## Remediation summary

Blockers received: 2

Blockers fixed: 2

Blockers remaining: 0

Verification conflicts: 0

Escalations: 0

New follow-up candidates: 0

READY FOR SOL RE-REVIEW
