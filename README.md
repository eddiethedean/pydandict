# PydanDict

[![CI](https://github.com/eddiethedean/pydandict/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/pydandict/actions/workflows/ci.yml)
[![Read the Docs](https://readthedocs.org/projects/pydandict/badge/?version=latest)](https://pydandict.readthedocs.io/)
[![PyPI](https://img.shields.io/pypi/v/pydandict.svg)](https://pypi.org/project/pydandict/)
[![Python versions](https://img.shields.io/pypi/pyversions/pydandict.svg)](https://pypi.org/project/pydandict/)
[![License](https://img.shields.io/pypi/l/pydandict.svg)](https://github.com/eddiethedean/pydandict/blob/main/LICENSE)

**Pydantic models. Mapping APIs. Validated changes.**

PydanDict adds a validated mapping surface to Pydantic models. `DictModel` is a
genuine `BaseModel` and `MutableMapping[str, object]`, so attribute access and
mapping access operate on one state boundary.

- **One state:** `record.age` and `record["age"]` read and write the same field.
- **Atomic updates:** coupled fields validate together and rejected changes roll back.
- **Mapping-native reads:** keys, views, `get`, unpacking and `dict(record)` work directly.
- **Guarded descendants:** supported nested containers route writes through root validation.
- **Pydantic integration:** schemas, aliases, serializers and FastAPI remain available.

> **Release status:** 0.3.0 is the latest published release. It was published from
> the immutable `v0.3.0` tag and is available on [PyPI](https://pypi.org/project/pydandict/0.3.0/).
> See the [release record](https://pydandict.readthedocs.io/en/latest/release/).

## Install

PydanDict supports Python **3.11–3.14** and pins its direct runtime dependency to
**`pydantic==2.13.4`**. The package is alpha software under the MIT license.

```sh
python -m pip install pydandict
```

For a development checkout, install the optional tooling and integration stack:

```sh
python -m pip install -e ".[dev]"
```

FastAPI, HTTPX, Pyright and the test/build tools are optional development or
integration dependencies; ordinary library use requires only Pydantic.

## Quick start

```python
from collections.abc import Mapping, MutableMapping

from pydantic import BaseModel, Field, ValidationError
from pydandict import DictModel


class User(DictModel):
    name: str
    age: int = Field(ge=0)


user = User(name="Eddie", age=40)
user["age"] = 41

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
print(dict(user))
```

Output:

```text
{'name': 'Eddie', 'age': 41}
```

## Read the full guides

The detailed examples and contracts live in the published documentation site:

- [Getting started](https://pydandict.readthedocs.io/en/latest/getting-started/)
- [API specification](https://pydandict.readthedocs.io/en/latest/api/)
- [Mutation and transaction semantics](https://pydandict.readthedocs.io/en/latest/mutation-semantics/)
- [Nested values and ownership](https://pydandict.readthedocs.io/en/latest/nested-values/)
- [Pydantic/FastAPI compatibility](https://pydandict.readthedocs.io/en/latest/compatibility/)
- [Typing strategy](https://pydandict.readthedocs.io/en/latest/typing/)
- [Testing and acceptance strategy](https://pydandict.readthedocs.io/en/latest/testing/)

## Supported contract at a glance

| Area | Supported behavior |
| --- | --- |
| Mapping identity | `DictModel` is a Pydantic model and mutable mapping with canonical string keys. |
| Writes | Assignment, `update` and `|=` validate a candidate state before committing. |
| Defaults/extras | Defaults are visible; declared fields are protected; extras require `extra="allow"`. |
| Serialization | Use Pydantic `model_dump`, `model_dump_json` and JSON Schema for serialized output. |
| Nested values | Use `MutableSequence`, `MutableMapping` and `MutableSet` within the closed ownership envelope. |
| Runtime policy | Python 3.11–3.14, exact Pydantic 2.13.4, no async or persistence API. |

Important boundaries: concrete mutable annotations (`list`, `dict`, `set`),
arbitrary objects, custom scalar subclasses/timezones, stored ordinary BaseModels,
trusted construction and pickle restoration are unsupported. There is no shared
writer/thread-safety guarantee. See the [compatibility limits](https://pydandict.readthedocs.io/en/latest/compatibility/)
before building an integration.

## Migration

From 0.1.0, replace mutable annotations recursively:

| Previous | Supported |
| --- | --- |
| `list[T]` | `collections.abc.MutableSequence[T]` |
| `dict[K, V]` | `collections.abc.MutableMapping[K, V]` |
| `set[T]` | `collections.abc.MutableSet[T]` |

Specialize generic models explicitly. In 0.3.0, non-string `pop` keys raise
`TypeError` even with a fallback. Use a string mutation key or `get` for a
read-only fallback. See the [migration contract](https://pydandict.readthedocs.io/en/latest/phase-0.2-plan/)
and [changelog](https://github.com/eddiethedean/pydandict/blob/main/CHANGELOG.md).

## Development

After installing `.[dev]`, run from the repository root:

```sh
PYTHONPATH=src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q
python tools/check_typing.py
python -m pyright --verifytypes pydandict --ignoreexternal
ruff check src tests tools/check_typing.py tools/qualify_package.py tools/benchmark.py tools/check_doc_examples.py
ruff format --check src tests tools/check_typing.py tools/qualify_package.py tools/benchmark.py tools/check_doc_examples.py
python tools/check_docs.py
python tools/check_doc_examples.py
```

Build the documentation locally with `python -m mkdocs build --strict`. The
release workflow uses the same docs configuration through [Read the Docs](https://pydandict.readthedocs.io/).
See the [contribution guide](https://github.com/eddiethedean/pydandict/blob/main/CONTRIBUTING.md),
[roadmap](https://github.com/eddiethedean/pydandict/blob/main/ROADMAP.md),
[release policy](https://pydandict.readthedocs.io/en/latest/release/) and
[private security reporting policy](https://github.com/eddiethedean/pydandict/blob/main/SECURITY.md).
