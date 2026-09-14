# Integrated Pydandict prototype

**Phase 0.1 starting baseline — development version `0.1.0.dev0`.**

This local experiment implements the difficult model/mapping, transaction and
ownership mechanisms together. Its import is `pydandict_prototype`, deliberately
separate from the future production `pydandict` package. It is not a supported
release and has not been published.

## Run it

From the repository root, using `uv` and an available Python 3.14 interpreter:

```sh
uv venv --python 3.14 .venv
uv pip install --python .venv/bin/python -r prototypes/requirements.txt
PYTHONPATH=prototypes .venv/bin/python -m pytest prototypes/tests -q
.venv/bin/python prototypes/run_checks.py
```

Reuse an existing environment if already set up. Python 3.11 also passes the runtime
suite. The full harness uses POSIX environment paths and was run on macOS ARM64;
Windows/Linux qualification is still future work. It builds a wheel and sdist,
rebuilds a wheel from the sdist, and runs two consumers in separate temporary
virtual environments outside the checkout. It also checks installed public types,
expected type errors and initial performance/retention behavior. It requires package
index access to prepare those environments; it never uploads a distribution.

Results are written to [the evidence JSON](../docs/research/prototype-results.json).
See [the findings and limitations](../docs/research/prototype-findings.md) before
using the design as a production implementation.

## Small example

Prefer standard mutable ABC annotations for honest runtime types. The private
owned containers implement those protocols, rather than inheriting built-in storage.

```python
from collections.abc import MutableSequence
from typing import Self

from pydantic import Field, ValidationError, model_validator
from pydandict_prototype import DictModel


class Budget(DictModel):
    ceiling: int = Field(default=10, ge=0)
    costs: MutableSequence[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def within_budget(self) -> Self:
        if sum(self.costs) > self.ceiling:
            raise ValueError("costs exceed ceiling")
        return self


budget = Budget(costs=[2])
handle = budget.costs
handle.append(3)
assert budget["costs"] is handle

try:
    handle.append(100)
except ValidationError:
    assert list(handle) == [2, 3]

budget.update(ceiling=20, costs=[8, 9])
assert budget.model_dump() == {"ceiling": 20, "costs": [8, 9]}

try:
    handle.append(1)
except RuntimeError:
    pass  # Replacing costs made the earlier handle stale.
```

Concrete `list`/`dict`/`set` annotations also supply Pydantic schemas, but the owned
runtime values are protocol guards. They do not satisfy `isinstance(value, list)`
or analogous concrete-container checks. Use `MutableSequence`, `MutableMapping`
and `MutableSet` annotations when consumer typing must match the actual runtime
interface. Use model serialization for a detached payload; `dict(model)` is shallow
and preserves owned references.

## Layout

- [Transaction/model adapter](pydandict_prototype/_core.py): one authoritative model
  state, canonical validation, schema/serialization hooks, ownership reconciliation,
  pointer-swap commit and public mapping/lifecycle methods.
- [Private containers](pydandict_prototype/_containers.py): ordinary sequence,
  mapping and set methods routed through the owning root.
- [Tests](tests/test_prototype.py), [method inventory](tests/test_inventory.py),
  [stateful oracle](tests/test_stateful.py): success, rejection, injected commit
  failures, escaped references, integration and generated sequences.
- [Library consumer](consumers/library_consumer.py) and
  [FastAPI consumer](consumers/fastapi_consumer.py): public imports only.
- [Strategy controls](compare_strategies.py), [benchmarks](benchmark.py), and
  [qualification harness](run_checks.py): reproducible observations.

Private attributes, custom initialization/post-init hooks, writable properties,
ordinary nested BaseModels, arbitrary objects and cyclic values are rejected by
this prototype. Validators must be deterministic, safe on canonical Python state,
and idempotent on untouched values; topology-changing transformations of retained
owned containers are rejected when detected. See the findings for the full boundary.
