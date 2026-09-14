# Phase 0.3 — Embedded ingress blocker remediation

Scope: SOL-017 from the [fourth independent review](phase-0.3-rereview-4.md).
SOL-015 was verified fixed by that review and is not reopened. SOL-011 remains
an unrelated follow-up; no follow-up implementation is included.

## Root cause and implementation

The outer identity function-after validator prevented pydantic-core from reusing
the public mode-dispatch validator for embedded model-shaped schemas. Embedding
then used only the native JSON branch, losing the Python input guard. Field/output
detachment could not reject original unsupported values after coercion.

[Compatibility boundary](../../src/pydandict/_compat.py): keep json-or-python
dispatch at the compiled public root, allowing embedded model nodes to reuse the
guarded public validator. Canonical/alias/Python rewrites instead explicitly
compile their own model nodes: temporarily suppress prebuilt reuse during
synchronous compilation and restore every original class completion flag in
finally, including compilation exceptions/BaseException. No validator callbacks
run during compilation; no shared-writer/thread-safety promise is added.

This uses the existing checked, pinned compatibility boundary, not framework
monkeypatching, exception replay, unconditional strictness, a serialization
round-trip or another transaction engine. Pydantic-core's prebuilt exclusion of
function-after/wrap roots is described in its
[primary implementation](https://github.com/pydantic/pydantic-core/blob/main/src/validators/prebuilt.rs);
the actual behavior is verified against the required Pydantic 2.13.4/core 2.46.4.

Source/API impact: restore the existing rejection of arbitrary attribute objects
and custom scalar subclasses in ordinary BaseModel/TypeAdapter collection
envelopes. Supported dictionary coercion, native JSON/strings, aliases/context,
guarded nested values and canonical transactions remain supported. No new public
API, persisted format, dependency, workflow or version change; no data migration.

## Verification contract

Protected [fourth-review test](../../tests/test_sol_phase03_rereview_4.py) remains
unchanged, SHA-256 `79526f011654109adc42ac14a625510906aa10d599e4858b2106ade2dd82b200`.
Its four cases failed before the fix and pass after it, preserving standalone
rejection/supported-input controls. The protected third-review tests also remain
unchanged, SHA-256 `a0bab3487285dc2b91a0d171c6f1064f69f9e1b82275beb587c9598ed0749bd0`.

[Implementation controls](../../tests/test_phase03_embedding_remediation.py)
add 14 cases: embedded mixed field-specific JSON strictness, strict strings,
before/wrap/after callback source isolation and mode/context, and compiler
completion-flag restoration after TypeError/KeyboardInterrupt with subsequent
canonical nested mutation. No exact callback-count guarantee is prescribed.
The qualification inventory adds the four blocker nodes and explicit embedded
Python ingress applicability/exclusions without changing existing AC proof.

Local results: all 580 tests pass in 108.78s, including both deterministic
100-example × 100-step stateful machines. Focused results: 417 retained/native
compatibility cases pass; all 18 new blocker/control cases pass. Required
lint/format (34 files), strict positive/exact four negative typing and public
completeness 100% pass. Docs: 54 Markdown files, 302 local links, eight examples,
zero errors; whitespace check passes.

SOL-017 implementation status: FIXED, pending exact-candidate clean artifact/CI
reconciliation and independent Sol confirmation. Artifact/CI results will be
reconciled to the committed candidate below before final handoff. Historical
qualification records remain unchanged; do not reuse their older source hashes
as verification of this fix.

Independent approval remains a Sol responsibility; this implementation report
does not declare an independent review PASS or authorize package publication.
