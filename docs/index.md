# PydanDict

## Pydantic models with validated mapping semantics

PydanDict lets one schema-defined object work naturally with both Pydantic and
mapping-oriented code. `DictModel` is a genuine `BaseModel` and
`MutableMapping[str, object]`: attribute access and canonical-key access share
one validated state boundary.

[![PyPI](https://img.shields.io/pypi/v/pydandict.svg)](https://pypi.org/project/pydandict/)
[![CI](https://github.com/eddiethedean/pydandict/actions/workflows/ci.yml/badge.svg)](https://github.com/eddiethedean/pydandict/actions/workflows/ci.yml)
[![Read the Docs](https://readthedocs.org/projects/pydandict/badge/?version=latest)](https://pydandict.readthedocs.io/)

The current published release is **0.3.0**. See the [release record](release.md#030-release-record)
for the tag, qualification evidence and PyPI package.

## Why PydanDict?

| Capability | What it means |
| --- | --- |
| One state | `record.age` and `record["age"]` address the same field. |
| Atomic writes | Assignment, `update` and `|=` validate a candidate before commit. |
| Mapping reads | Keys, live views, `get`, unpacking and `dict(record)` work directly. |
| Guarded descendants | Supported mutable children route changes through root validation. |
| Native Pydantic | Fields, aliases, serializers, JSON Schema and FastAPI remain available. |

## Install

PydanDict supports Python 3.11–3.14 and pins its direct runtime dependency to
`pydantic==2.13.4`.

```sh
python -m pip install pydandict
```

For the development and integration stack:

```sh
python -m pip install -e ".[dev]"
```

## Choose a path

| If you want to… | Start with… |
| --- | --- |
| Build your first model | [Getting started](getting-started.md) |
| Look up mapping methods and errors | [API specification](api.md) |
| Understand rollback and ownership | [Mutation semantics](mutation-semantics.md) and [nested values](nested-values.md) |
| Integrate with Pydantic or FastAPI | [Compatibility](compatibility.md) |
| Add strict consumer typing | [Typing strategy](typing.md) |
| Understand the project’s requirements | [Product](product.md) and [architecture](architecture.md) |
| Verify or release a change | [Testing](testing.md) and [release automation](release.md) |

The [documentation guide](https://github.com/eddiethedean/pydandict/blob/main/docs/README.md)
explains the status vocabulary and how the design contracts, implementation
plans and historical evidence fit together.

## 0.3.0 support envelope

The release is intentionally focused. It supports scalar fields, explicitly
specialized generics, and the existing finite nested ownership envelope using
`MutableSequence`, `MutableMapping` and `MutableSet` annotations.

The following are outside the contract: concrete mutable annotations
(`list`, `dict`, `set`), arbitrary objects, custom scalar subclasses/timezones,
ordinary `BaseModel` values stored as descendants, trusted construction, pickle
restoration, persistence and shared writer/thread-safety guarantees. Read the
[compatibility limits](compatibility.md) before relying on behavior beyond the
qualified envelope.

## Project status

Phase 0.3 passed independent release review and was published from the immutable
[`v0.3.0` tag](https://github.com/eddiethedean/pydandict/tree/v0.3.0). The project
is alpha software: documented support is evidence-backed, while broader feature
ideas remain on the [roadmap](https://github.com/eddiethedean/pydandict/blob/main/ROADMAP.md).

For source, contribution and security information, visit the
[GitHub repository](https://github.com/eddiethedean/pydandict),
[contribution guide](https://github.com/eddiethedean/pydandict/blob/main/CONTRIBUTING.md)
and [security policy](https://github.com/eddiethedean/pydandict/blob/main/SECURITY.md).
