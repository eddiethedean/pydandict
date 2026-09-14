"""SOL-017: embedded native schemas must retain the closed Python ingress contract."""

from types import SimpleNamespace

import pytest
from pydantic import BaseModel, TypeAdapter

from pydandict import DictModel


class ScalarRecord(DictModel):
    value: int


class PlainEnvelope(BaseModel):
    child: ScalarRecord


class ScalarSubclass(int):
    pass


@pytest.mark.parametrize("embedding", ["ordinary-model", "adapter-list"])
@pytest.mark.parametrize("source_kind", ["scalar-subclass", "attribute-source"])
def test_sol017_embedded_python_ingress_rejects_unsupported_sources(embedding, source_kind):
    source = (
        {"value": ScalarSubclass(2)}
        if source_kind == "scalar-subclass"
        else SimpleNamespace(value=2)
    )
    # The standalone entry already enforces the same required rejection.
    with pytest.raises(TypeError, match="^pydandict_unsupported_value:"):
        TypeAdapter(ScalarRecord).validate_python(source, from_attributes=True)

    adapter = TypeAdapter(PlainEnvelope if embedding == "ordinary-model" else list[ScalarRecord])
    supported = {"child": {"value": "2"}} if embedding == "ordinary-model" else [{"value": "2"}]
    result = adapter.validate_python(supported, from_attributes=True)
    child = result.child if embedding == "ordinary-model" else result[0]
    assert isinstance(child, ScalarRecord) and child.value == 2

    unsupported = {"child": source} if embedding == "ordinary-model" else [source]
    with pytest.raises(TypeError, match="^pydandict_unsupported_value:"):
        adapter.validate_python(unsupported, from_attributes=True)
