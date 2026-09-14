# SOL-017 / FINAL-001: native strings ingress investigation

Status: **fix implemented; local runtime/static verification passed**. This investigation
does not constitute an independent production-review PASS or final release approval.

Investigated source: `5cb5587990ba96d535c9b970406b99e28aa4cabc`.
Runtime: Python 3.11.14, Pydantic 2.13.4, pydantic-core 2.46.4.

## Required invariant

Phase 0.3 AC-002 requires rejection of unsupported original input, including
custom scalar subclasses and string enums, before coercion can erase their
types. AC-001 and the inherited construction-mode compatibility contract also
require preserving native coercion, strictness, validation options, callback
information, and errors. Fixing one requirement by breaking the other is not a
resolution.

`Record(DictModel)` with `value: int` currently accepts a `str` subclass or
string enum containing `"2"` through strings validation, while Python
validation rejects the same unsupported input. The defect also occurs through
`TypeAdapter(Record)` and under an ordinary `BaseModel` envelope. The existing
post-validation detachment cannot detect a source type after conversion to an
ordinary integer.

Executable regression: `tests/test_phase03_strings_ingress.py`.

Executed:

```sh
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest \
  tests/test_phase03_strings_ingress.py \
  tests/test_sol_phase03_rereview_4.py -q
```

Result: **6 failed, 4 passed**. The six failures are the expected missing
`TypeError`; the previous embedded Python-ingress verification still passes.
No required gate was disabled. This was the pre-fix result; production remediation
is described below.

## Rejected implementation mechanisms

These are concrete local probes against the pinned runtime, not assertions
that every possible design is impossible.

| Mechanism | Observed compatibility problem |
| --- | --- |
| Insert an identity before-validator before an integer schema | Native strings validation accepts `"2"` with `strict=True`; the before-validator version raises `int_type`. The callback changes the input representation passed to the inner validator. |
| Audit in a callable discriminator with a single tagged-union choice | Native coercion is retained, but invalid input changes the error location from `()` to `('audit',)`. An internal audit must not become a public error-path component. |
| Re-enter a child through a separate native strings validator | An embedded before-model callback sees `info.field_name == 'child'` and `info.data == {'earlier': 1}`. Standalone re-entry sees `None` for both. Forwarding public keyword options alone does not preserve the parent validation state. |

The last observation invalidates the proposed dedicated strings-entry bridge
as a transparent fix **without further design and verification**. It must not
be described as implemented or validated.

A Pydantic entry-point plugin is not an automatic solution: its entry hook runs
at the outer validator, which may belong to an ordinary model or collection.
Auditing that entire input would impose DictModel's closed-value policy on
unrelated outer fields. Locating only the applicable DictModel inputs must also
respect aliases, unions, and user callbacks; a naive schema walk would duplicate
Pydantic's routing semantics. A plugin or process-wide API patch therefore needs
an explicit architectural review rather than being slipped in as a local guard.

## Implemented resolution

The native model boundary now uses the callable-discriminator audit. It checks
the complete original DictModel input with the existing closed-value clone and
discards that clone; Pydantic validates its original native input with the
original validation state. This enforces AC-002 without re-entering validation.
Canonical Python validation removes this native audit from its rewritten schema.

The internal audit tag is omitted from generated JSON Schema and public error
locations. The error adapter retains the original Rust ValidationError payload
by assigning an empty-slots subclass with the same native layout. Its `errors`,
`json`, `str`, and `repr` views remove only the audit location component. It does
not reconstruct rendered custom-error messages or discard their contexts, input
mode, hide-input setting, or actual line errors. Native error relays therefore
remain meaningful to Pydantic.

This requires a deliberate expansion within the pinned compatibility boundary:
the adapter wraps Pydantic's model, dataclass, TypeAdapter and plugin validator
factories. Schemas containing an audit or a validation callback receive an entry
wrapper which forwards all arguments directly to their existing validator. The
callback case is necessary because an ordinary model callback can relay a
DictModel error; Pydantic retains the native line-error payload during that relay.
Schemas with neither an audit nor a callback retain their original validator.
Existing factory implementations remain the delegates. No plugin entry point,
dependency change, dependency fork, validation-option replay or process-global
validation context is introduced.

The wrapper prevents the pinned runtime's prebuilt-validator reuse for affected
model entries. Embedded schemas carry their own original-input audit and existing
callback/field detachment, so they enforce the closed input policy even without
that optimization. Mutation/canonical validators remain separate and unchanged
in their required behavior. This integration and the equal error-layout
assumption must be requalified when changing the pinned Pydantic version.

The focused regression file now passes **19 tests**, including all six original
failures, native strict dates, parent callback information/context, every public
error projection for native parsing/custom/ValueError failures, nested error
relays, literal backslash aliases, and ordinary-envelope fields which must retain
Pydantic's acceptance of string subclasses. The earlier native/embedded matrix
also passed **372 tests** after schema-generation compatibility was corrected.

The first full runtime attempt passed 585 cases and failed its source-provenance
benchmark because production source was edited while the benchmark was running.
That is a verification orchestration error, not a product failure; no gate was
weakened. The subsequent complete run held production source fixed and passed
**599 tests in 100.13s**, including the required complete benchmark. Strict
positive/exact-negative typing passed, public type completeness was 100%, Ruff
lint/format passed for the required 35-file inventory, and the documentation
checker passed 57 Markdown files, 304 local links and 11 Python examples.
An isolated Python 3.14 environment with the same pinned Pydantic/core also
passed the **385-test** focused ingress/native/embedding matrix, including the
native error-layout adapter and protected Sol verification.

The verified production/test bytes were committed as
`b919462ae6ab1eb01e9dd684a6b493360767c305`. A clean detached checkout of that
commit passed fresh direct and sdist-rebuilt wheel qualification: **31 commands**,
isolated imports/library/scalar/HTTP consumers, installed metadata, public
completeness, positive typing and exactly four expected negative diagnostics per
wheel. [Actual artifact evidence](phase-0.3-strings-ingress-artifacts.json) retains
that measured source, command outputs, dependencies and artifact hashes. Earlier
records were preserved. The initial artifact attempt selected an older system
Python for Pyright and failed to find `typing.assert_type`; setting the Python
3.11 toolchain PATH resolved that environmental failure without changing a gate.

Python 3.14's focused matrix used interpreter **3.14.3** with Pydantic 2.13.4 and
core 2.46.4. Other OS/interpreter lanes still require CI execution; local checks
do not claim they ran.

The release still requires normal production review followed by the independent
final release check. Historical approvals and measurements refer to their actual
earlier source revisions, not this remediation.
