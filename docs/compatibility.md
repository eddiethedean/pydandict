# Pydantic and FastAPI compatibility

## Policy and baseline

The [Phase 0.1 findings](research/prototype-findings.md) record implemented
compatibility on the pinned experimental stack. The matrix below remains the
production target. V1 targets Pydantic v2 only. Exact dependency bounds remain G4 work; no version
range is supported merely because it is v2. The planning probes use Python
3.11.14, Pydantic 2.13.4, FastAPI 0.141.1, and Pyright 1.1.411. These are locally
observed versions, not a declaration that they are the latest releases or a tested
Pydandict support matrix. See [upstream evidence](research/upstream-behavior.md).

Use normal `BaseModel` control classes for differential tests. Classify differences
as intentional, unsupported pending a gate, or bugs. Publish that classification
with each release instead of claiming total drop-in equivalence.

## Feature matrix

| Area | Intended contract | Required check / limitation |
| --- | --- | --- |
| Identity | Real BaseModel and mapping ABC instance | Runtime and static assertions |
| Construction | Standard annotations, `Field`, `Annotated`, Python/JSON/strings validation | Guard installation on every path |
| Coercion and strictness | Follow configured Pydantic validation in the relevant mode | Python and JSON modes may differ |
| Defaults | Pydantic default/factory evaluation; defaults validated | Pydandict requires validation of defaults |
| Extras | Pydantic input policy, documented mutation policy | No shadowed methods or unsafe values |
| Aliases | Input/output boundaries retain Pydantic alias rules | Mapping uses canonical field names |
| Validators | Standard field/model validator forms under rerunnable-state contract | G2; no blanket compatibility claim |
| Nested types and unions | Preserve schema and active branch validation | G3 ownership restrictions apply |
| Frozen fields/models | Reject both direct and descendant mutation | Stronger descendant protection than plain frozen BaseModel |
| Private attributes | Excluded from mapping and schema-state guarantee | No mutable private dependency for invariants |
| Computed fields | Attribute/serialization features, not stored mapping keys | Invalidate supported caches after commit |
| Serialization | Use Pydantic serializer paths | Guards must not change payload shape or leak internals |
| JSON Schema | Standard model schema in validation/serialization modes | No ownership metadata or wrapper-only definitions |
| Copy | Validated updates; independent mutable ownership | Intentional shallow-copy divergence |
| Trusted construction | Proposed `model_construct` rejected in v1 | Intentional narrower API |
| Equality | Preserve Pydantic model equality | Not ordinary dictionary equality |
| Iteration | Keys | Intentional change from BaseModel pairs |

## Serialization and schemas

Keep `model_dump`, `model_dump_json`, `model_json_schema`, and ordinary Pydantic
adapters available. Mapping reads return live Python values and do not invoke
serializers. Test fields that are excluded, renamed, computed, secret-valued,
date/decimal/UUID-valued, nested, generic, and discriminated-union members.

Pydantic distinguishes Python-mode output and JSON-compatible serialization, with
field/model serializers and inclusion controls; see the
[serialization documentation](https://docs.pydantic.dev/latest/concepts/serialization/).
Pydandict's proposal is to preserve those boundaries. A custom model serializer
may return a non-dictionary; that does not change the mapping key set.

Check `exclude_unset`, `exclude_defaults`, `exclude_none`, `by_alias`, serialization
context, round-trip options, and subclass-field filtering against a BaseModel
control. Never implement these by iterating `items()` and assuming serialization
is equivalent. Internal guards and transaction metadata must not appear in schema,
repr, dumps, or OpenAPI. JSON Schema should express the model's fields, constraints,
required keys, and configured extra policy, not its transaction implementation.

Alias choices/paths and generators require explicit input/output fixtures.
Pydantic documents distinct validation and serialization alias controls in its
[alias guide](https://docs.pydantic.dev/latest/concepts/alias/). The proposed v1
namespace policy additionally rejects a stored extra whose name collides with an
active emitted alias, and rejects ambiguous field serialization aliases. Detect
generator results during schema setup where possible. A custom serializer that
creates new collisions is trusted application code and must handle its own output.

## Unsafe and inherited surfaces

Pydantic `model_copy(update=...)` and `model_construct` are trusted-data paths in
the [BaseModel API](https://docs.pydantic.dev/latest/api/base_model/); the baseline
probe demonstrates their unchecked behavior. Proposed Pydandict copy validates
the resulting model and its ownership, while public construct is rejected. This
tradeoff must be prominent in migration notes.

Audit deprecated `copy`, `construct`, `parse_obj`, and other inherited convenience
methods. Proposed deprecated `copy()` with only supported update/deep arguments
delegates to validated `model_copy` and preserves a deprecation warning; reject
include/exclude operations that could produce an incomplete model. Deprecated
`construct` must reach the disabled trusted path, never create an unsafe instance.
Inherited validated parsing may remain if it reaches safe construction.

`copy.copy`, `copy.deepcopy`, and nested copy/adoption need independent ownership
tests. Pickle loading bypasses ordinary constructors and is not a v1 persistence
feature; reject unsupported restoration rather than allow an apparently valid
model with absent guards. Reflection and explicit base-method bypass are outside
the supported contract.

Public metadata accessors that normally expose mutable containers should return
detached containers where specified in the mutation contract. Code that directly
edits `model_extra` must migrate to validated mapping writes.

## FastAPI acceptance

FastAPI's [request-body](https://fastapi.tiangolo.com/tutorial/body/) and
[response-model](https://fastapi.tiangolo.com/tutorial/response-model/) documentation
describe Pydantic model integration. Being a BaseModel subclass is necessary for
our intended path, but does not prove that mixed mapping inheritance and guards
work correctly in every encoding path.

Test actual HTTP requests with `TestClient`:

1. Parse a valid request into the declared `DictModel`; verify ABC and model identity.
2. Reject invalid input with the framework's expected 422 validation response.
3. Mutate through the mapping surface and return through `response_model` and
   return-annotation variants; verify serialized output.
4. Test aliases, extra rejection, response filtering, nested lists/models, and
   `response_model_exclude_unset` after mutations and resets.
5. Inspect `/openapi.json` for field constraints, required fields, aliases, and
   model references; compare with a corresponding BaseModel endpoint.
6. Test `jsonable_encoder`, a nested DictModel inside an ordinary BaseModel,
   collections of DictModel responses, and custom field/model serializers.
7. Verify application mutation exceptions are handled intentionally. Do not promise
   that a `ValidationError` raised inside an endpoint automatically becomes a 422;
   framework request validation and application errors are different paths.

Do not require a FastAPI plugin, monkey patch, special encoder, or response adapter
for the supported use cases. Returning a raw framework `Response` bypasses its
normal model processing and is not evidence of compatibility.

## Release matrix

Proposed Python target starts at 3.11, subject to actual packaging/support review.
At release time test the selected minimum and newest supported Python, the chosen
minimum and latest supported Pydantic v2 minor, and supported FastAPI bounds with
compatible Starlette/httpx versions. Use a prerelease dependency lane as an early
warning, without implying prerelease support. Bound dependencies by evidence and
document any private-API reliance in release notes.

Additionally smoke-test every advertised intermediate Python minor and each claimed
OS (initial candidates: Linux, macOS, Windows). Maintain a versioned matrix recording
Python, platform, Pydantic, its resolved pydantic-core, FastAPI/Starlette/httpx and
Pyright, plus exact commands and results. Keep development pins reproducible while
package dependency bounds express the actually tested support policy. Do not add
a separately incompatible pydantic-core constraint.

Pyright is the required checker. Other checkers and Python implementations may be
evaluated later but have no launch support claim without fixtures. New upstream
failures receive a minimal reproducer and an adapter assessment; do not expand
dependency bounds until supported cases pass.
