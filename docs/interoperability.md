# Interoperability goals and limits

## Generic consumers

PydanDict should work with existing code whose contract is a Python mapping, with
no import or special-case branch in that consumer. This includes reads via `[]`,
`get`, key membership, keys/items/values, iteration, length, dictionary construction,
and keyword unpacking. Runtime `Mapping` and `MutableMapping` recognition and static
assignment are both acceptance requirements.

The [Python collection ABC documentation](https://docs.python.org/3/library/collections.abc.html)
defines the required mapping primitives and mixins. PydanDict must supply explicit
transactional overrides for mutating mixins whose ordinary implementation could
partially modify a constrained model.

## Consumer compatibility table

| Consumer expectation | Target | Qualification |
| --- | --- | --- |
| `Mapping[str, object]` reads | Supported | Keys are canonical names; values are live Python objects |
| `isinstance(value, Mapping)` | Supported | Actual ABC participation required |
| `MutableMapping[str, object]` writes | Supported with validation | Schema constraints can reject otherwise legal dictionary edits |
| `dict(value)` / `{**value}` | Supported shallow copy | Descendant values can remain attached to the model |
| `fn(**value)` | Supported when function accepts those keys | Values may not match the function's own annotations |
| Mapping structural pattern match | Targeted test | Key space excludes computed/private fields |
| Model-aware Pydantic/FastAPI consumer | Supported target | Follow tested compatibility matrix |
| Pair iteration expected from BaseModel | Intentional break | Use `value.items()` |
| Equality to arbitrary dict | Intentional difference | Compare `dict(value)` if content equality is intended |
| Arbitrary key deletion / clear | Restricted | Declared fields remain present |
| Concrete `dict` check or built-in/C mutation primitives | Outside scope | Explicit conversion at that consumer boundary |
| `json.dumps(value)` without an encoder | Not promised | Use `model_dump_json()` or JSON-mode dump |
| Dict union operators / `fromkeys` | Outside v1 surface | Use plain dictionaries or validated construction |

## Two meaningful integration fixtures

**Existing read consumer:** a function taking only `Mapping[str, object]`, using
`items`, `get`, and membership. Pass a DictModel directly and run strict Pyright.
Verify defaults and extras appear while computed/private data do not.

**Existing write consumer:** a function taking only `MutableMapping[str, object]`,
calling `update` to change coupled fields. Demonstrate one valid update and one
invalid update that leaves state intact. Document that generic mutability is
subject to the record schema, just as some mappings restrict writable keys.

Framework-specific libraries should be advertised only after testing their actual
code paths. Some accept `Mapping` in one function and require `dict` in another.
Do not infer ecosystem-wide compatibility from one successful `dict(model)` call.

## Migration guidance

For an internal dictionary, define a `DictModel` schema, construct through validated
input, and retain existing mapping-oriented reads and writes. Replace mutations
that intentionally create incomplete intermediate state with one `update`. Replace
deleting a defaulted field with `reset`. Decide extras policy explicitly and check
that nested field types fit the supported ownership envelope.

For an existing Pydantic model, changing its base class is an opt-in migration.
Review field-name collisions, pair iteration, equality expectations, default
validation, mutable nested BaseModel values, unsafe copy/construct usage, and
metadata edits. No automatic conversion helper or global patch is planned in v1.

At a concrete-dict boundary, choose deliberately between a shallow `dict(model)`
and a serialized `model_dump(mode='json')`. The latter may apply aliases, filters,
or custom serializers and is not a substitute for access to live model fields.
