# Proposed API specification

This is the Phase 0.1 package API. The original executable prototype remains under
`prototypes/pydandict_prototype`; its [findings](research/prototype-findings.md)
identify tested behavior and deliberate limitations. See [decision status](decisions/README.md)
before treating a contract as final.

## Definition and construction

The public import is `from pydandict import DictModel`. The conceptual inheritance
is `class DictModel(BaseModel, MutableMapping[str, object])`; this is not a complete
implementation. Metaclass, iterator typing, and method-resolution details are G1.

Declare fields with standard annotations, `Field`, `Annotated`, and Pydantic
configuration. Use keyword construction or `Model.model_validate(mapping)` for
mapping input. Do not add a positional-dict constructor in v1. Standard validation
entry points, including JSON and strings modes, retain their Pydantic purposes.

Proposed default configuration is `extra='forbid'`, `validate_assignment=True`,
and `validate_default=True`. Validation cannot be disabled for `DictModel`.
Explicit `validate_assignment=False`, model/field `validate_default=False`, or
an equivalent supported bypass configuration must fail class setup rather than
quietly weakening the contract. Other supported Pydantic configuration remains
available; ownership limitations are separate from schema configuration.

## Key space

Keys are canonical declared field names followed by allowed extra names. Declared
fields appear in Pydantic field order, including values supplied by defaults.
Extras follow insertion order; overwriting does not move a key, deleting and
reinserting an extra appends it. All keys must be strings.

Aliases are accepted by Pydantic validation as configured and used by serialization
as configured. They do not become alternate mapping keys. A field
`user_id: int = Field(alias='userId')` is addressed as `m['user_id']`. In mapping
operations `userId` is not resolved to the field; if it is not another canonical
field, it is an ordinary extra name governed by the extras policy. Input/output
alias collisions, including an extra named `userId`, must be diagnosed before
they can produce ambiguous serialized data; see [compatibility](compatibility.md).

Private attributes, `ClassVar`, computed fields, properties, caches, and Pydantic
internals are not mapping entries. `Field(exclude=True)` fields **are** entries:
serialization exclusion does not change model state or mapping visibility.

Reject declared field names that shadow mapping methods or protected model
attributes, including `items`, `keys`, `values`, `get`, `update`, `reset`, and
`model_dump`. Use a safe canonical name plus an alias for external schemas.
Allowed extras must also not shadow this namespace, private names, or computed
properties. Detect conflicts in class creation or input validation, not on a later
method call. Canonical fields take precedence over alias interpretation during
mutation.

## Read operations

| Operation | Result / behavior |
| --- | --- |
| `m[key]` | Current Python field/extra value; absent or non-string key raises `KeyError` |
| `m.field` | Same authoritative field value; unknown attribute raises `AttributeError` |
| `iter(m)` | Iterator of canonical string keys |
| `len(m)` | Number of fields plus stored extras |
| `key in m` | Key membership; false for non-string or absent key |
| `m.get(key, default=None)` | Existing value or supplied default; does not validate/insert default |
| `m.keys()` | Live `KeysView[str]` |
| `m.values()` | Live `ValuesView[object]` |
| `m.items()` | Live `ItemsView[str, object]` |
| `dict(m)` | New shallow dictionary of keys and live Python values |
| `m.model_dump(...)` | Pydantic serialization, including configured aliases/exclusions/serializers |

Views observe subsequent committed changes. An iterator captures a structural
version and raises `RuntimeError` if keys change before it finishes. Replacing
values without a key change does not invalidate the key iterator; no snapshot
consistency is promised across multiple reads. `bool(m)` follows `len(m)`.

## Mutation surface

Signatures below summarize behavior; final overloads must also satisfy Pyright and
the ABC typeshed contracts. Values are accepted as `object` and validated at runtime.

| Operation | Return | Contract |
| --- | --- | --- |
| `m[key] = value` / `m.field = value` | None | One validated transaction |
| `m.update(other=(), /, **kwargs)` | None | Mapping or iterable of pairs; one transaction for the merged input |
| `m \|= other` | Same `Self` | Same accepted input forms and transaction as `update` |
| `m.setdefault(key, default=None)` | `object` | Return existing value, or validate/insert and return stored value |
| `del m[key]` / `del m.field` | None | Remove allowed extra; reject declared field deletion |
| `m.pop(key[, default])` | `object` or default | Remove existing extra; reject existing declared field even with a default argument |
| `m.popitem()` | `tuple[str, object]` | Attempt last key in defined order; reject if protected; `KeyError` if empty |
| `m.clear()` | None | Remove all entries atomically; reject if any declared fields exist |
| `m.reset(*field_names)` | None | Restore named defaults atomically; no arguments means no-op |
| `m.model_copy(update=None, deep=False)` | New `Self` | Proposed validated copy; no mutation of original |

Successful `pop`/`popitem` returns of mutable values are detached and usable;
previously borrowed handles into removed state become stale. Preparing the return
value is part of the transaction. See [ownership](nested-values.md#snapshots-copies-and-escape-paths).

`update` consumes input fully before validation. Later duplicate keys win; keyword
arguments win over the positional source. A malformed pair, failing generator, or
non-string write key aborts without changes. `update(m)` is supported. Empty
`update`, `|= {}`, `reset()`, and `clear()` on an already empty model are no-ops.
See the [mutation matrix](mutation-semantics.md) for validation and error precedence.

V1 does not define `m | other`, `other | m`, `fromkeys`, or a dict-like `copy` method.
Use `dict(m) | other` for an ordinary dictionary or validated `model_copy` for a
model. Inherited deprecated Pydantic `copy` must be explicitly handled as described
in [compatibility](compatibility.md), not accidentally mistaken for `dict.copy`.

## Error contract

- `KeyError`: missing mapping lookup/deletion/pop without fallback; empty `popitem`.
- `AttributeError`: missing attribute reads/deletes.
- `TypeError`: non-string mutation key, malformed method invocation, disabled
  trusted construction, or unsupported ownership/type configuration. Malformed
  iterable pairs follow Python's `TypeError`/`ValueError` distinction.
- `pydantic.ValidationError`: invalid values, forbidden extra writes, protected
  field deletion/reset, frozen mutation, and model/parent constraint failure.
- `RuntimeError`: reentrant transaction on the same root, stale nested handle,
  or structural mutation during iteration.

Preserve Pydantic error details and locations where they exist. Library-specific
validation errors should use stable documented codes such as
`pydandict_field_deletion` and `pydandict_reset_required`, constructed through public
Pydantic error facilities. Exact codes are to be finalized by the error prototype;
never wrap all exceptions as `ValidationError`. A validator's programming error
must propagate with the live state intact.

## Equality and hashing

Preserve Pydantic model equality, including its treatment of model type, extra
values, and private attributes. Do not equate a model and an arbitrary dictionary
merely because their keys/values match. This deliberately differs from common
mapping implementations and must be documented for consumers.

Mutable `DictModel` instances are unhashable. Frozen models follow a separately
tested Pydantic-compatible hash path only when all stored values are safely
immutable and hashable. Do not cache hashes across mutable state.
