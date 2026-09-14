# Product definition and scope

## Established purpose

Pydandict makes Pydantic models first-class Python mappings. Its one primary
abstraction is `DictModel`, a real Pydantic `BaseModel` whose fields can be read
and changed through both attribute syntax and mapping syntax.

The package serves two audiences:

| Audience | Current friction | Desired outcome |
| --- | --- | --- |
| Application developer | Generic mapping consumers cannot directly use ordinary model APIs | Pass one model to mapping-oriented code and Pydantic-oriented code |
| Package author | An internal dictionary can drift away from its schema after initial validation | Keep dictionary-oriented code while validating every supported state change |

Existing `BaseModel` classes do not become mappings automatically. Developers
opt into `DictModel` when defining a model. Consumers that already accept the
mapping contract should not need to import Pydandict or recognize its type.

## Representative use cases

- A renderer iterates `record.items()` while an API endpoint uses the same record
  as its response model.
- A library keeps timeout and retry settings in a schema-defined mapping and
  applies several coordinated changes with atomic `update`.
- A plugin host stores constrained metadata fields plus explicitly allowed extras.
- A pipeline maintains a nested configuration whose parent validators must remain
  true when child values change.

These are schema-defined records. A homogeneous arbitrary-key store is already
well served by other abstractions and does not justify a public `TypedMap` in v1.

## Established requirements

1. Preserve the names **Pydandict**, import package `pydandict`, and `DictModel`.
2. Preserve genuine `BaseModel` identity and Pydantic/FastAPI integration.
3. Implement the mapping protocol with keys from iteration and meaningful runtime
   ABC checks, plus useful static compatibility with Pyright.
4. Store one authoritative model state, accessible through either syntax.
5. Validate supported mutations continuously; reject failure without corrupting
   the live model. Include deletion, bulk changes, and reachable mutable values.
6. Use Pydantic's validation machinery and metadata rather than a parallel schema
   language, serializer, or validation engine.
7. Keep v1 small enough to audit and adopt as a dependency.

## V1 scope

The required core includes model construction, mapping reads/views, attribute and
mapping writes, atomic bulk updates, controlled destructive operations, extras,
defaults, aliases, field/model validators, serialization/schema, ownership of
supported nested values, and typing/integration evidence.

Proposed additions are one explicit `reset(*field_names)` operation and validated
copy handling. These close concrete default/copy safety gaps; they are not a
general transaction-builder API.

Out of scope: public typed collection families, replacement `TypedDict`, persistence,
reactive subscriptions, storage engines, async validators, schema inference,
Pydantic v1 support, monkey-patching existing models, automatic `from_model`
conversion, framework plugins, and a promise of exact built-in `dict` behavior.

## Success criteria

A v1 candidate must demonstrate a mapping-only consumer and a FastAPI endpoint
using the same model without conversion, strict Pyright consumer checks, failed
transaction rollback, and protected nested values with parent validation. All
declared support claims must correspond to passing tests on a published matrix.

Prefer measured dependency size, import time, and mutation cost over speculative
speed claims. Adoption goals are qualitative until prototypes establish a baseline:
small public API, clear migration, no application framework requirement, and
errors that explain why a state change was rejected.

## Honest positioning

“Pydantic models with dictionary semantics” is the primary description. Avoid
“works anywhere a dict works,” “all Pydantic behavior is unchanged,” and “can
never be invalid.” Those claims obscure concrete-dict consumers, deliberate
protocol changes, unsafe Python reflection, and user-defined validator behavior.

The intended guarantee is validation across supported public mutation paths for
supported owned values, under the documented validator contract. This must not
be reduced to top-level assignment validation and advertised as lifetime safety.
