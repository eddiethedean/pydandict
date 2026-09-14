"""Additional compatibility coverage for SOL-004's storage and cache contracts."""

import pytest
from pydantic import Field

from pydandict import DictModel, _compat


def test_canonical_validator_is_class_local_and_rebuilt():
    class Parent(DictModel):
        number: int = Field(alias="input_number")

    class Child(Parent):
        pass

    parent = _compat.canonical_validator(Parent)
    assert _compat.canonical_validator(Parent) is parent
    child = _compat.canonical_validator(Child)
    assert child is not parent
    assert Parent.model_rebuild(force=True)
    assert _compat.canonical_validator(Parent) is not parent
    assert _compat.canonical_validator(Child) is child
    model = Parent(input_number=1)
    model.number = "2"
    assert model.number == 2 and model.model_dump(by_alias=True) == {"input_number": 2}


@pytest.mark.parametrize(
    "slot,value",
    [
        ("__dict__", {1: "invalid storage key"}),
        ("__pydantic_extra__", []),
        ("__pydantic_fields_set__", ["number"]),
    ],
)
def test_corrupt_required_storage_fails_closed(slot, value):
    class Record(DictModel):
        number: int

    # Private candidate allocation lets this exercise a corrupt upstream slot
    # without using a supported public operation to corrupt an owned root.
    model = _compat.blank_model(Record, {"number": 1}, {"number"})
    object.__setattr__(model, slot, value)
    accessor = {
        "__dict__": _compat.raw_state,
        "__pydantic_extra__": _compat.raw_extra,
        "__pydantic_fields_set__": _compat.fields_set,
    }[slot]
    with pytest.raises(TypeError, match=r"^pydandict_incompatible_pydantic:"):
        accessor(model)


def test_malformed_consumed_model_schema_fails_before_compilation():
    with pytest.raises(TypeError, match=r"^pydandict_incompatible_pydantic:"):
        _compat.compile_validator({"type": "model", "cls": DictModel, "schema": None})


def test_json_schema_metadata_is_not_treated_as_validator_nodes():
    example = {"type": "model", "cls": "documentation"}

    class Record(DictModel):
        value: int = Field(alias="input_value", json_schema_extra={"examples": [example]})

    model = Record(input_value=1)
    model.value = 2
    assert model.model_dump(by_alias=True) == {"input_value": 2}
    assert Record.model_json_schema()["properties"]["input_value"]["examples"] == [example]
    assert Record.model_rebuild(force=True)
    assert Record.model_validate({"value": 3}, by_alias=False, by_name=True).value == 3


def test_rebuild_resolves_forward_references_in_its_callers_namespace():
    class Record(DictModel):
        value: "Later"

    Later = int
    assert Record.model_rebuild()
    assert Record(value="3").value == 3
    assert Later is int


@pytest.mark.parametrize("mode", ["python", "json", "strings"])
def test_public_validation_completes_deferred_schemas_before_adapter_access(mode):
    class Record(DictModel):
        value: "Later"

    Later = int
    if mode == "python":
        model = Record.model_validate({"value": "3"})
    elif mode == "json":
        model = Record.model_validate_json('{"value": "3"}')
    else:
        model = Record.model_validate_strings({"value": "3"})
    assert model.value == 3
    assert Later is int
