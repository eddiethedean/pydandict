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

SOL-017 implementation status: FIXED; exact-candidate clean artifact/CI results
are reconciled below. Independent Sol confirmation remains required. Historical
qualification records remain unchanged; do not reuse their older source hashes
as verification of this fix.

Independent approval remains a Sol responsibility; this implementation report
does not declare an independent review PASS or authorize package publication.

## Exact-candidate closure

Status: SOL-017 FIXED; zero known blockers remaining. SOL-015 remains verified fixed.
Candidate: `4bf376e73c29be66a152f9a4904669428bee36fd`. [All 11 CI jobs passed](https://github.com/eddiethedean/pydandict/actions/runs/34897109410).
[Fresh artifact record](../research/phase-0.3-embedding-artifacts.json) retains 31 actual
external direct/rebuilt build/install/consumer/static commands, installed imports,
metadata outputs, dependency freezes and measured hashes.
[Execution reconciliation](../research/phase-0.3-embedding-execution.json) supplies
all 580 actual node IDs, 46 component hashes, every AC's resolved proof and
11 executed/non-applicable cells, real job/log/version/dependency evidence,
behavioral exclusions, failures and limitations. Historical records are unchanged.

| Executed CI job | Resolved CPython | Result |
| --- | --- | --- |
| [Documentation checks](https://github.com/eddiethedean/pydandict/actions/runs/34897109410/job/104153844786) | 3.11.16 | Passed |
| [Production artifact qualification (Python 3.14)](https://github.com/eddiethedean/pydandict/actions/runs/34897109410/job/104153845067) | 3.14.7 | Passed |
| [Compatibility (windows-latest, Python 3.14)](https://github.com/eddiethedean/pydandict/actions/runs/34897109410/job/104153845159) | 3.14.7 | Passed |
| [Production artifact qualification (Python 3.11)](https://github.com/eddiethedean/pydandict/actions/runs/34897109410/job/104153845169) | 3.11.16 | Passed |
| [Compatibility (ubuntu-latest, Python 3.11)](https://github.com/eddiethedean/pydandict/actions/runs/34897109410/job/104153845177) | 3.11.16 | Passed |
| [Compatibility (ubuntu-latest, Python 3.14)](https://github.com/eddiethedean/pydandict/actions/runs/34897109410/job/104153845240) | 3.14.7 | Passed |
| [Compatibility (windows-latest, Python 3.11)](https://github.com/eddiethedean/pydandict/actions/runs/34897109410/job/104153845251) | 3.11.9 | Passed |
| [Compatibility (ubuntu-latest, Python 3.12)](https://github.com/eddiethedean/pydandict/actions/runs/34897109410/job/104153845262) | 3.12.14 | Passed |
| [Compatibility (macos-latest, Python 3.11)](https://github.com/eddiethedean/pydandict/actions/runs/34897109410/job/104153845266) | 3.11.9 | Passed |
| [Compatibility (ubuntu-latest, Python 3.13)](https://github.com/eddiethedean/pydandict/actions/runs/34897109410/job/104153845311) | 3.13.15 | Passed |
| [Compatibility (macos-latest, Python 3.14)](https://github.com/eddiethedean/pydandict/actions/runs/34897109410/job/104153845466) | 3.14.7 | Passed |

Every runtime job reports 580 passed, strict positive/exact negative typing
success and public completeness 100%, with lint/format also green. Both artifact
jobs report qualified direct/rebuilt consumers and complete their benchmark step.
Release-only preflight remains intentionally non-applicable on push.

| AC | Resolved proof nodes | Actual job kinds |
| --- | --- | --- |
| AC-001 | 265 | runtime |
| AC-002 | 53 | runtime |
| AC-003 | 14 | runtime |
| AC-004 | 14 | runtime |
| AC-005 | 9 | runtime |
| AC-006 | 59 | runtime |
| AC-007 | 42 | runtime |
| AC-008 | 29 | runtime |
| AC-009 | 42 | runtime |
| AC-010 | 39 | runtime |
| AC-011 | 38 | runtime |
| AC-012 | 53 | runtime |
| AC-013 | 30 | runtime |
| AC-014 | 52 | runtime |
| AC-015 | 31 | runtime |
| AC-016 | 43 | runtime |
| AC-017 | 2 | runtime |
| AC-018 | 20 | runtime |
| AC-019 | 3 | runtime |
| AC-020 | 360 | runtime |
| AC-021 | 14 | runtime |
| AC-022 | 1 | runtime |
| AC-023 | 0 | runtime |
| AC-024 | 0 | artifact |
| AC-025 | 1 | artifact, docs, runtime |
| AC-026 | 1 | runtime |
| AC-027 | 13 | runtime |
| AC-028 | 0 | artifact, docs |

Command-only artifact/static/docs proof is separate from pytest nodes. Expected
rejection is tested, not labeled omitted; Python objects/subclasses cannot be
carried by JSON/StringsInput. Before/wrap/after native callback isolation,
embedded native strictness and compiler cleanup have additional actual proof nodes.

| Artifact measurement | Sdist SHA-256 | Direct wheel SHA-256 | Rebuilt wheel SHA-256 |
| --- | --- | --- | --- |
| Local CPython 3.11.14 | `84ce018b4a3c1c51255191f7688806f12c956321edb414ce0198813a51e92927` | `29244a96b3064a0312f34f9eccbd1255534ab5d6141017ef34dd71bfd9389f65` | `0851dc27fe99fd91689f801d032a26e0ef84ba56a25d84af395395d8a951f066` |
| CI CPython 3.14.7 | `5b60e4faf81f0a0bf175aabe4e7451c2abf694174742b21539736db2708ee46e` | `90798f23d1a890db862a5518e75ff6ff411575a9a7ec47d5dee1ba2018df4800` | `f1a73828b4b788f0a3859300e206550f10a80be2201245632196fed6b068a856` |
| CI CPython 3.11.16 | `c019c07f7b205633ea6aa6b85102a723f2426347f54c4859a3052425f22c20e8` | `7b644a7f296970bb4392d55063211c8c55ae799e795984820f3fdf9d6ebcefcd` | `7b644a7f296970bb4392d55063211c8c55ae799e795984820f3fdf9d6ebcefcd` |

Nonblocking upstream Starlette/httpx/anyio and action-runtime deprecation notices
are recorded, not hidden. No dependency/workflow expansion, follow-up remediation
or publication occurred. Local full/static execution preceded the source commit
and is explicitly byte-reconciled; clean exact-candidate CI independently repeats
those gates. The following handoff commit changes only documentation and does
not silently relabel the measured source/artifact identities.

Final handoff: READY FOR SOL RE-REVIEW. Independent Sol approval remains required.

Final documentation check: 54 Markdown files, 304 local links, eight Python
examples, zero errors. All 46 measured component hashes still match after this
documentation-only reconciliation; whitespace verification passes.
