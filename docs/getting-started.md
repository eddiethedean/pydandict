# Getting started

This guide covers the supported 0.3.0 workflow: install `pydandict`, define a
Pydantic model with mapping behavior, make validated changes, and hand the model
to ordinary Pydantic/FastAPI code.

## Install

PydanDict supports Python 3.11–3.14 and pins its direct runtime dependency to
`pydantic==2.13.4`.

```sh
python -m pip install pydandict
```

FastAPI, HTTPX, Pyright and the test/build tools are development or optional
integration dependencies. Install them when working from a checkout:

```sh
python -m pip install -e ".[dev]"
```

## Define one model, use two interfaces

`DictModel` is both a Pydantic `BaseModel` and a mutable mapping. Attribute and
canonical-key access address the same validated state.

```python
from collections.abc import Mapping

from pydantic import Field
from pydandict import DictModel


class User(DictModel):
    name: str
    age: int = Field(ge=0)


user = User(name="Eddie", age=40)
assert user.age == user["age"] == 40
assert isinstance(user, Mapping)
assert dict(user) == {"name": "Eddie", "age": 40}
```

Mapping keys are canonical field names in declaration order, followed by allowed
extras. A field alias such as `userId` is accepted at Pydantic validation and
serialization boundaries, but it is not an alternate mapping key.

## Make atomic changes

Single writes and `update` both validate before committing. Use one `update` when
an invariant spans multiple fields:

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
bounds.update(low=5, high=8)
before = dict(bounds)
try:
    bounds.update(low=9, high=4)
except ValidationError:
    assert dict(bounds) == before
```

Input pairs are consumed completely before validation, so malformed or failing
iterables cannot partially apply a batch. `record |= changes` has the same
transaction semantics as `update`.

## Defaults, extras and copies

Declared fields cannot be deleted. `reset` restores selected defaults, while
`model_copy` returns a validated independent model. Enable extras explicitly when
you need open-ended metadata:

```python
from pydantic import ConfigDict
from pydandict import DictModel


class Settings(DictModel):
    model_config = ConfigDict(extra="allow")
    retries: int = 3


settings = Settings()
settings["environment"] = "production"
clone = settings.model_copy()
clone["environment"] = "staging"
settings.reset("retries")
assert settings["environment"] == "production"
```

`dict(model)` is a shallow mapping copy. Use `model_dump` or
`model_dump_json` when you need Pydantic aliases, serializers or exclusion rules.

## Nested mutable values

Use mutable ABC annotations for supported owned containers:
`MutableSequence`, `MutableMapping` and `MutableSet`. Do not use concrete
`list`, `dict` or `set` annotations for mutable fields. Stored descendants are
guarded by the root model's validation boundary, and caller-owned input is
detached during construction.

The ownership envelope is deliberately finite. Arbitrary objects, custom scalar
subclasses, ordinary `BaseModel` values stored as descendants, thread safety and
persistence are outside the 0.3.0 contract. See [nested values](nested-values.md)
and [compatibility limits](compatibility.md).

## Continue with the reference docs

- [API specification](api.md) for the complete mapping and error contracts.
- [Mutation semantics](mutation-semantics.md) for transaction and rollback rules.
- [Typing](typing.md) for consumer annotations and negative cases.
- [FastAPI/Pydantic compatibility](compatibility.md) for integration behavior.
- [Release and support policy](release.md) for versioned evidence and boundaries.
