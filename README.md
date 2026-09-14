# PydanDict

[![CI](https://github.com/eddiethedean/pydandict/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/pydandict/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pydandict.svg)](https://pypi.org/project/pydandict/)
[![Python versions](https://img.shields.io/pypi/pyversions/pydandict.svg)](https://pypi.org/project/pydandict/)
[![License](https://img.shields.io/pypi/l/pydandict.svg)](https://github.com/eddiethedean/pydandict/blob/main/LICENSE)

**Pydantic models. Mapping APIs. Validated changes.**

Define a record once, use it through attributes or mapping-oriented code, and keep
its supported state valid as it changes. `DictModel` is a genuine Pydantic
`BaseModel` and a `MutableMapping[str, object]`—not a wrapper around a second
dictionary.

- **One state:** `record.age` and `record["age"]` read and write the same field.
- **Atomic updates:** coupled fields validate together; rejected changes leave
  committed values and model metadata unchanged.
- **Mapping-native reads:** keys, live views, `get`, unpacking and `dict(record)`
  work without calling serializers.
- **Protected descendants:** supported nested containers and child models route
  mutations through the root validation boundary.
- **Explicit lifecycle:** reset defaults and make validated, independent model copies.
- **Pydantic integration:** retain supported fields, constraints, aliases,
  serializers, JSON Schema and FastAPI integration on the pinned stack.

> **Release status:** 0.2.0 is the latest published release. This checkout prepares
> 0.3.0, whose Phase 0.3 contract passed independent review. Publication requires
> successful final-candidate CI and artifact checks. No 0.3.0 tag or
> publication has occurred. See [release readiness](docs/research/release-0.3.0-readiness.md).

## Install

Python **3.11–3.14**; the sole direct runtime dependency is
**`pydantic==2.13.4`**. The package is alpha software, licensed under MIT.

Install the published package:

```sh
python -m pip install pydandict
```

To work with the prepared 0.3.0 checkout, run this from the repository root:

```sh
python -m pip install -e ".[dev]"
```

The examples below describe this checkout's supported contract. FastAPI and
testing/build tools are development or optional integration dependencies, not
requirements for ordinary library use.

## Quick start

```python
from collections.abc import Mapping, MutableMapping

from pydantic import BaseModel, Field, ValidationError
from pydandict import DictModel


class User(DictModel):
    name: str
    age: int = Field(ge=0)


user = User(name="Eddie", age=40)

assert user.name == user["name"] == "Eddie"
user["age"] = 41
assert user.age == 41

try:
    user.age = -1
except ValidationError:
    assert user.age == 41
else:
    raise AssertionError("invalid age was accepted")

assert isinstance(user, BaseModel)
assert isinstance(user, Mapping)
assert isinstance(user, MutableMapping)
assert list(user) == ["name", "age"]
assert dict(user) == {"name": "Eddie", "age": 41}
```

Pydantic supplies schemas and validation. PydanDict adds canonical key iteration
and an isolated transaction boundary around supported writes.

## Use existing mapping-oriented code

No conversion or PydanDict-specific branch is needed for a consumer that accepts
a `Mapping`:

```python
from collections.abc import Mapping


def describe(record: Mapping[str, object]) -> str:
    return ", ".join(f"{key}={value}" for key, value in record.items())


assert describe(user) == "name=Eddie, age=41"
assert user.get("missing", "fallback") == "fallback"
assert {**user} == {"name": "Eddie", "age": 41}
```

Keys are canonical field names in declaration order, followed by allowed extras
in insertion order. Defaults and serialization-excluded fields remain mapping
entries. Views are live; unfinished key iterators are invalidated by committed
key/order changes, not value-only updates.

`dict(record)` is a **shallow mapping copy**, not serialization or a detached
nested payload. Use `model_dump` or `model_dump_json` for Pydantic serialization.

## Change related fields atomically

A valid final state may require changing more than one field. `update` validates
the merged candidate as a whole instead of assigning fields one at a time.

```python
from typing import Self

from pydantic import Field, ValidationError, model_validator
from pydandict import DictModel


class Bounds(DictModel):
    low: int = Field(default=1, ge=0)
    high: int = Field(default=3, ge=0)

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.low > self.high:
            raise ValueError("low must not exceed high")
        return self


bounds = Bounds()
bounds.update(low=5, high=8)  # A single low=5 write would fail against high=3.
assert dict(bounds) == {"low": 5, "high": 8}

before = dict(bounds)
try:
    bounds.update(low=9, high=4)
except ValidationError:
    assert dict(bounds) == before
else:
    raise AssertionError("invalid batch was accepted")
```

`update` accepts mappings, pairs and keyword arguments. Later duplicates win;
keywords take precedence over positional input. Inputs are fully consumed before
commit, so malformed pairs or a late iterable exception cannot partially apply a
batch. `record |= changes` uses the same transaction and retains model identity.

Validators must be safe to rerun on canonical state. Whole-root revalidation can
repeat callbacks; external side effects are not rolled back.
See [validator and transaction semantics](docs/mutation-semantics.md).

## Defaults, extras and copies

```python
clone = bounds.model_copy(update={"high": 10})
assert clone is not bounds
assert clone.high == 10 and bounds.high == 8

bounds.reset("low", "high")
assert dict(bounds) == {"low": 1, "high": 3}
assert bounds.model_fields_set == set()
```

Declared fields cannot be deleted—even when optional or defaulted. Use `reset`
to restore selected defaults. Required fields have no reset value.

Unknown input is forbidden by default. Enable `ConfigDict(extra="allow")` to
store extras; extras can be inserted and removed through mapping operations.
Unknown writes under `extra="ignore"` still fail rather than disappear silently.

| Operation | Behavior |
| --- | --- |
| `record[key] = value` / `record.field = value` | Validate and commit one candidate state |
| `record.update(...)` / `record \|= changes` | Apply a batch atomically |
| `record.setdefault(key, default)` | Return the existing value without validating an unused default, or validate insertion |
| `record.pop(key[, default])` / `del record[key]` | Remove an allowed extra; declared fields are protected |
| `record.popitem()` | Attempt the last key; do not skip a protected declared field |
| `record.clear()` | Remove extras atomically on a fieldless model; declared fields prevent clearing |
| `record.reset(*names)` | Reevaluate selected defaults atomically; no names means no-op |
| `record.model_copy(update=...)` | Return a new validated model; leave the source unchanged |

For a complete defaults/extras/metadata workflow, run
[`examples/library_config.py`](examples/library_config.py).

## Keep supported nested values guarded

Use mutable ABC annotations, not concrete `list`/`dict`/`set` annotations.
Ordinary built-in inputs are still accepted; stored values expose guarded ABC
interfaces.

```python
from collections.abc import MutableSequence
from typing import Self

from pydantic import ValidationError, model_validator
from pydandict import DictModel


class Cart(DictModel):
    budget: int
    costs: MutableSequence[int]

    @model_validator(mode="after")
    def within_budget(self) -> Self:
        if sum(self.costs) > self.budget:
            raise ValueError("costs exceed budget")
        return self


source = [2, 3]
cart = Cart(budget=10, costs=source)
source.append(100)  # Caller input is detached from stored state.
assert list(cart.costs) == [2, 3]

cart.costs.append(4)
try:
    cart.costs.append(2)  # Valid integer, invalid parent state.
except ValidationError:
    assert list(cart.costs) == [2, 3, 4]
else:
    raise AssertionError("parent constraint was bypassed")
```

`MutableMapping`, `MutableSet` and nested `DictModel` fields follow the existing
closed ownership envelope. Replacing/removing an owned node can make previously
borrowed handles stale. This is not arbitrary mutable-object support or thread
safety; see [nested values and ownership](docs/nested-values.md).

## Separate mapping state from serialized output

Aliases belong to validation/serialization boundaries, not alternate mapping keys.
Serialization exclusion is not access control for mapping readers.

```python
from pydantic import Field
from pydandict import DictModel


class Account(DictModel):
    user_id: int = Field(alias="userId")
    token: str = Field(exclude=True)


account = Account(userId=7, token="private")
assert account["user_id"] == 7 and "userId" not in account
assert "token" in account
assert account.model_dump(by_alias=True) == {"userId": 7}
```

Standard supported serializers, filters and serialization context remain
Pydantic's responsibility. A custom serializer may produce a non-dictionary
payload without changing mapping membership.

## FastAPI integration

With the optional pinned `fastapi==0.141.1` integration dependency installed,
use ordinary model annotations. This example uses `User` from the quick start:

```python
from fastapi import FastAPI

app = FastAPI()


@app.post("/users", response_model=User)
def create_user(user: User) -> User:
    user.update(age=user.age + 1)
    return user
```

Request validation, response serialization and OpenAPI are covered by the pinned
integration tests. No special encoder or framework plugin is required for the
supported paths. See [compatibility](docs/compatibility.md).

## Deliberate differences and support limits

| Compared with | Important difference |
| --- | --- |
| `dict` | A model is a mutable mapping, not a built-in dictionary; model equality does not become dict equality |
| `dict` | Keys must be strings; declared fields cannot disappear; no binary `\|`, `fromkeys` or dict-style `copy` API |
| `BaseModel` | Iteration yields canonical keys, not key/value pairs |
| `BaseModel` | `model_copy(update=...)` validates updates and detaches supported mutable descendants even with `deep=False` |
| `BaseModel` | Trusted `model_construct`/deprecated `construct` and pickle are disabled |
| Plain frozen models | Frozen ancestors/fields also protect supported descendant writes |

Qualified scalar leaves are exact `None`, `bool`, `int`, `float`, `str`, `bytes`,
`Decimal`, `date`, `datetime`, `time`, `timedelta` and `UUID` types. Temporal
timezone values must be absent or exact `datetime.timezone` instances.
Supported nullable/unions, `Literal`, `Annotated` constraints and explicitly
specialized generics stay within the closed envelope. `Any`, `object` and extras
do not bypass input/output safety checks.

Arbitrary objects, ordinary `BaseModel` values stored inside a `DictModel`,
enums, custom scalar subclasses/timezones and concrete mutable field annotations
are unsupported. Ordinary BaseModel envelopes *containing* a DictModel are a
separate supported integration. Custom initialization/finalizers,
`model_post_init`, private attributes and writable properties are also outside
the supported hook contract.

Attribute types retain their declared precision. Generic mapping values are
`object` and require narrowing; automatic per-key type inference is not promised.
See [typing](docs/typing.md). There is no async API, persistence feature or shared
writer/thread-safety guarantee. Validation uses trusted schemas; deliberate
reflection/base-method bypass is not a security sandbox.

## Migration

From 0.1.0, replace mutable annotations recursively:

| Previous annotation | Supported annotation |
| --- | --- |
| `list[T]` | `collections.abc.MutableSequence[T]` |
| `dict[K, V]` | `collections.abc.MutableMapping[K, V]` |
| `set[T]` | `collections.abc.MutableSet[T]` |

Specialize generic models explicitly. The outer
`__pydantic_extra__: dict[str, V]` metadata declaration remains valid.
See the [0.2 migration contract](docs/phase-0.2-plan.md#annotation-and-owned-value-envelope).

For 0.3.0, non-string `pop` keys raise `TypeError` even with a fallback. Use string
mutation keys, or `get` when a read-only fallback is intended. Native JSON/strings
and supported embedded ingress retain their documented validation boundaries.
No persisted-data migration is required; see the [changelog](CHANGELOG.md).

## Documentation and development

- [API reference](docs/api.md) and [mutation semantics](docs/mutation-semantics.md)
- [Nested ownership](docs/nested-values.md), [compatibility](docs/compatibility.md) and [typing](docs/typing.md)
- [Phase 0.3 contract](docs/phase-0.3-plan.md), [passed review](docs/reviews/phase-0.3-rereview-5.md) and [release preparation](docs/release.md#030-release-preparation)
- [Documentation index](docs/README.md), [roadmap](ROADMAP.md) and [contributing](CONTRIBUTING.md)

After installing `.[dev]`, run from the repository root:

```sh
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q
python tools/check_typing.py
PYTHONPATH=src python -m pyright --verifytypes pydandict --ignoreexternal
ruff check src tests tools/check_typing.py tools/qualify_package.py tools/benchmark.py
ruff format --check src tests tools/check_typing.py tools/qualify_package.py tools/benchmark.py
python tools/check_docs.py
```

Artifact qualification is a separate clean, committed-source check:
`python tools/qualify_package.py`. Follow the [release checklist](docs/release.md)
before tagging; historical evidence does not automatically qualify a later commit.

Use the [private security reporting route](SECURITY.md) for vulnerabilities.
The package is [MIT licensed](LICENSE).
