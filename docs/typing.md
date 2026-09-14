# Typing strategy: Pyright first

## Public target

`DictModel` is assignable to both `Mapping[str, object]` and
`MutableMapping[str, object]`, while remaining assignable to `BaseModel`.
Normal Pydantic field declarations retain attribute inference and constructor
checking. The package ships a `py.typed` marker and avoids a required
checker plugin or generated per-model files for the base experience.

Pyright describes typed-library packaging and completeness checks in its
[typed libraries guide](https://github.com/microsoft/pyright/blob/main/docs/typed-libraries.md).
The release pipeline should type-check the installed distribution, not only source
files in the repository.

## Phase 0.1 and Phase 0.2 evidence

The [prototype](research/prototype-findings.md) passes installed strict consumer
fixtures, four expected negative diagnostics and 100% public type completeness.
Owned mutable fields use private protocol guards. Prefer standard `MutableSequence`,
`MutableMapping` and `MutableSet` annotations for honest runtime typing; concrete
container annotations describe the input schema but do not establish concrete
runtime identity. Phase 0.2 enforces this contract at class creation: concrete
`list`, `dict` and `set` annotations (including nested and union occurrences)
fail with `pydandict_unsupported_annotation:` and an ABC migration hint. Generic
`DictModel` classes must be explicitly specialized before construction. The
strict gate analyzes every production source file, the positive fixture and the
typing, artifact and benchmark helpers; the negative fixture is checked independently against its four
expected diagnostics.

Private guards are generic over their payload and element/key/value types. Their
root coordinator uses typed callbacks with a generic return type. Transaction
paths and heterogeneous values use `object` with explicit narrowing. Pydantic's
dynamic schema operations remain in `_compat.py`; matching public validation
signatures retain Pydantic's `Any` boundary. Strict checking covers these private
contracts as well as the exported model surface.

## Heterogeneous mapping values

One model can contain an `int`, a `str`, and a nested model. Therefore the honest
base return type of `__getitem__(str)` is `object`. Writes accept `object` and
validate at runtime. `get` and `pop` overloads must follow missing-default behavior
without introducing `Any`; views carry string keys and object values.

Checked consumer fixture:

```python
from collections.abc import Mapping, MutableMapping
from typing import assert_type

from pydantic import BaseModel
from pydandict import DictModel


class User(DictModel):
    name: str
    age: int


user = User(name="Eddie", age=40)
model: BaseModel = user
record: Mapping[str, object] = user
editable: MutableMapping[str, object] = user

assert_type(user.age, int)
assert_type(user["age"], object)

age = user["age"]
if isinstance(age, int):
    next_age: int = age + 1

user["age"] = "41"  # Statically accepted object; Pydantic controls coercion.
```

Use `user.age += 1` for concise statically typed arithmetic. Without narrowing,
`user['age'] += 1` is not promised to pass strict Pyright. Attribute assignment of
`'41'` to an `int` field should be a static error even if runtime coercion would
accept it. Static types describe validated values, not all accepted input forms.

## Known inheritance conflict

Pydantic's `BaseModel.__iter__` yields `(name, value)` pairs. `Mapping.__iter__` must
yield keys. A subclass cannot preserve both iterator return contracts. Genuine
runtime model identity is achievable; perfect behavioral substitutability for
every `BaseModel` method is not.

G1 must prove that the public iterator is typed as `Iterator[str]` while all three
required assignments above pass. A narrowly scoped
`# pyright: ignore[reportIncompatibleMethodOverride]` on the intentional override
may be necessary in implementation. If needed, explain it at the override and
test the installed consumer surface. Do not suppress diagnostics project-wide,
pretend that iteration yields pairs in a stub, or redefine the public base as `Any`.

Nominal ABC inheritance is preferred. Virtual registration alone is not sufficient
for static assignability, and a structural protocol must not hide the requirement
that consumers using the standard ABCs can recognize the type.

## Limits and alternatives

Standard typing cannot automatically derive subclass-specific literal-key
overloads from arbitrary annotated fields. Runtime class generation or a
`dataclass_transform` does not supply that mapping to Pyright. V1 promises precise
attribute access and safe generic mapping access, not TypedDict-equivalent key
checking. This distinction must appear in the README and examples.

Handwritten literal-key overloads can be explored later, with a `str -> object`
fallback and compatible write signatures. Generated stubs are a possible optional
tool, not a v1 requirement. Do not narrow a subclass setter so it stops satisfying
`MutableMapping[str, object]`.

Mutable mappings are invariant in their value parameter. A heterogeneous
`DictModel` is not a `MutableMapping[str, int]`, even if one particular class happens
to contain only integer fields. Do not use casts to advertise that assignment.

Declared names must avoid mapping method collisions. Alias-friendly constructor
signatures, inherited fields, generic Pydantic models, `Annotated`, `Field` defaults,
and forward references all require fixtures. Custom nested guards must preserve
the declared API's type expectations or be excluded explicitly.

## Acceptance checks

Use strict Pyright with positive and negative fixtures. Assert attribute/read/view
types, `Self` returns, overload behavior, ABC assignment, and constructor errors.
Negative fixtures must verify the intended diagnostic rather than being ignored.
Check `model_copy()` preserves subclass type, `update()` returns `None`, and `|=`
retains the model type. Include a consumer that sees the value only as `BaseModel`
and document the iterator divergence.

Run `pyright --verifytypes pydandict --ignoreexternal` on the built and installed
package. The qualification helper runs this for both wheels. Target complete public annotations; a high completeness
score alone does not prove sound runtime behavior. The [testing plan](testing.md)
couples type fixtures to runtime examples.
