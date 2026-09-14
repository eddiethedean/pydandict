# PydanDict

[![CI](https://github.com/eddiethedean/pydandict/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/pydandict/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/pydandict.svg)](https://pypi.org/project/pydandict/)
[![Python versions](https://img.shields.io/pypi/pyversions/pydandict.svg)](https://pypi.org/project/pydandict/)
[![License](https://img.shields.io/pypi/l/pydandict.svg)](https://github.com/eddiethedean/pydandict/blob/main/LICENSE)

**Pydantic models with dictionary semantics.**

PydanDict is a Python library whose primary base class, `DictModel`, is
both a genuine Pydantic `BaseModel` and a Python mutable mapping. It is designed
to let existing mapping-oriented code consume models directly, and to let
package authors keep internal records valid as they change.

**Status: Phase 0.1 released.** The installable source package is in
[`src/pydandict`](src/pydandict/__init__.py), at release version `0.1.0`.
It was published to [PyPI](https://pypi.org/project/pydandict/0.1.0/) on
2026-09-13 from the immutable [`v0.1.0` tag](https://github.com/eddiethedean/pydandict/tree/v0.1.0).
It has 87 passing runtime tests, installed typing checks and working library/FastAPI
consumers in the recorded dependency envelope. See the [findings and limitations](docs/research/prototype-findings.md)
for exact evidence. The original [prototype guide](prototypes/README.md) remains
as a reproducible evidence fixture.

The plan prioritizes a dependable dependency: atomic failure behavior, protected
nested values, complete public typing, tested ecosystem compatibility, measured
costs, and verified distribution artifacts. Start with the
[roadmap](ROADMAP.md), [implementation work packages](docs/implementation-plan.md),
and [quality bar](docs/quality-bar.md). Qualification uses automated consumer
projects and maintainer checks; no external trials or participants are required.

Install the released package with `python -m pip install pydandict`. For a local
Phase 0.1 checkout, install the package and development tools with
`python -m pip install -e ".[dev]"`.

## One model, two ways to work

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
    user["age"] = -1
except ValidationError:
    assert user.age == 41  # Failed mutations leave the model unchanged.

assert isinstance(user, BaseModel)
assert isinstance(user, Mapping)
assert isinstance(user, MutableMapping)
assert list(user) == ["name", "age"]
assert dict(user) == {"name": "Eddie", "age": 41}
```

Attribute and mapping access address the same model state. Pydantic supplies
validation, field definitions, serializers, and JSON Schema. PydanDict supplies
mapping behavior and a transaction boundary around supported mutations.

## For existing Python systems

An API written against `Mapping[str, object]` should need no PydanDict-specific
branch, adapter, or `model_dump()` call:

```python
from collections.abc import Mapping


def describe(record: Mapping[str, object]) -> str:
    return ", ".join(f"{key}={value}" for key, value in record.items())


description = describe(user)
```

The target includes `[]`, `get`, containment, key iteration, live mapping views,
`dict(model)`, and keyword unpacking. It does not include `isinstance(model, dict)`
or compatibility with APIs that insist on a concrete built-in dictionary.
`dict(model)` is a shallow mapping copy; `model_dump()` is the serialization API.

## For package internals

```python
from pydantic import Field
from pydandict import DictModel


class RetryConfig(DictModel):
    timeout: float = Field(default=30.0, gt=0)
    retries: int = Field(default=3, ge=0)


config = RetryConfig()
config.update(timeout=60.0, retries=5)  # One validation transaction.
assert config.timeout == config["timeout"] == 60.0
```

Successful writes must satisfy the complete model contract. Failed writes must
preserve values and model metadata. Required fields cannot disappear; the
proposed deletion policy protects all declared fields, with an explicit `reset`
operation for defaults. Extras follow a documented Pydantic configuration policy.

**Continuous validation is a release requirement, including nested mutations.**
It cannot be delivered merely by enabling `validate_assignment`. The design
requires ownership and mutation guards for supported mutable values, validation
of affected parent constraints, and rejection of values that cannot be protected.
The exact supported value set and guard implementation remain Phase 0.2 hardening gates;
there is no silent fallback to unvalidated nested state. See
[mutation semantics](docs/mutation-semantics.md) and
[nested ownership](docs/nested-values.md).

## A Pydantic model for FastAPI

The intended integration uses ordinary model annotations:

```python
from fastapi import FastAPI

app = FastAPI()


@app.post("/users", response_model=User)
def create_user(user: User) -> User:
    user.update(age=user.age + 1)
    return user
```

Request parsing, response serialization, and OpenAPI should continue through
Pydantic. This is an acceptance target, with explicit integration tests required
before a release. See the [compatibility plan](docs/compatibility.md).

## Scope and typing

V1 centers on schema-defined `DictModel` records. It excludes a public `TypedMap`,
replacement `TypedDict`, generalized collection framework, persistence,
reactivity, and a new validation engine. Internal guards needed to protect model
fields are part of validation, not separate collection products.

Pyright support is a first-class requirement: attributes retain their declared
types, while generic mapping reads return `object` and require narrowing. Automatic
per-key inference such as `user["age"] -> int` is not promised by the base class.
See the [typing strategy](docs/typing.md).

## Read the plan

| Document | Purpose |
| --- | --- |
| [Phase 0.1 package](src/pydandict/__init__.py) | Installable `DictModel` implementation |
| [Phase 0.2 implementation contract](docs/phase-0.2-plan.md) | Bounded architecture, public contract, acceptance criteria and verification plan |
| [Prototype guide](prototypes/README.md) | Reproducible evidence commands and runnable example |
| [Prototype findings](docs/research/prototype-findings.md) | Demonstrated solutions, evidence and remaining limitations |
| [Documentation index](docs/README.md) | Reading paths and requirement traceability |
| [Product and scope](docs/product.md) | Audiences, use cases, success criteria |
| [Architecture](docs/architecture.md) | BaseModel integration and transactional state |
| [API specification](docs/api.md) | Mapping surface, names, return values, errors |
| [Mutation semantics](docs/mutation-semantics.md) | Invariants, atomicity, deletion, defaults, extras |
| [Nested values](docs/nested-values.md) | Ownership, escaped references, parent validation |
| [Typing](docs/typing.md) | Pyright, protocols, limitations, typing checks |
| [Compatibility](docs/compatibility.md) | Pydantic, serialization, schema, FastAPI |
| [Interoperability](docs/interoperability.md) | What existing consumers can and cannot assume |
| [Competition](docs/competitive-landscape.md) | Alternatives and focused positioning |
| [Testing](docs/testing.md) | Acceptance cases and release gates |
| [Roadmap](ROADMAP.md) | Sequenced implementation and release policy |
| [Implementation work packages](docs/implementation-plan.md) | Priorities, dependencies, first increments and stop criteria |
| [Quality bar](docs/quality-bar.md) | Measurable gates, automated consumer journeys and maintenance standards |
| [Release automation](docs/release.md) | Tag-gated checks, artifact build, and PyPI Trusted Publishing |
| [Security and performance](docs/security-performance.md) | Trust boundary, costs, benchmarks |
| [Decision log](docs/decisions/README.md) | Established requirements and proposed choices |
| [Upstream evidence](docs/research/upstream-behavior.md) | Sources and reproducible baseline observations |

## Contributing

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Design contributions should identify
the invariant they preserve and the acceptance test that will prove it. The next
work is Phase 0.2 hardening and contract finalization on the Phase 0.1 package.

The package is distributed under the MIT license; package-name ownership and the
private security reporting route remain pre-release checks. See [security reporting](SECURITY.md)
and the [changelog](CHANGELOG.md).
