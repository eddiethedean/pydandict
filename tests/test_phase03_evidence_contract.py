"""Implementation-side proof for the SOL-015 inventory's missing scalar anchors."""

import copy
import pickle
from collections.abc import Mapping, MutableMapping
from functools import cached_property

import pytest
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

from pydandict import DictModel
from tools import qualify_package


def test_scalar_iterator_structure_and_exhaustion_contract():
    class Record(DictModel):
        model_config = ConfigDict(extra="allow")
        value: int = Field(default=1, ge=0)

    record = Record()
    before_first = iter(record)
    record["extra"] = 2
    with pytest.raises(RuntimeError, match="pydandict_iterator_invalidated"):
        next(before_first)

    unchanged = iter(record)
    record.value = 3
    with pytest.raises(ValidationError):
        record.value = -1
    record.update()
    record.reset()
    assert list(unchanged) == ["value", "extra"]
    record["another"] = 4
    with pytest.raises(StopIteration):
        next(unchanged)

    after_first = iter(record)
    assert next(after_first) == "value"
    record.pop("extra")
    record["extra"] = 2
    with pytest.raises(RuntimeError, match="pydandict_iterator_invalidated"):
        next(after_first)


def test_scalar_model_equality_and_hash_contract():
    class Mutable(DictModel):
        model_config = ConfigDict(extra="allow")
        value: int

    first = Mutable(value=1, extra=2)
    assert first == Mutable(value=1, extra=2)
    assert first != Mutable(value=1, extra=3)
    assert first != {"value": 1, "extra": 2}
    with pytest.raises(TypeError):
        hash(first)

    class Frozen(DictModel):
        model_config = ConfigDict(frozen=True, extra="allow")
        value: int
        label: str

    class Control(BaseModel):
        model_config = ConfigDict(frozen=True, extra="allow")
        value: int
        label: str

    actual = Frozen(value=1, label="ready", extra=2)
    expected = Control(value=1, label="ready", extra=2)
    assert hash(actual) == hash(expected)
    assert actual == Frozen(value=1, label="ready", extra=2)
    assert actual != {"value": 1, "label": "ready", "extra": 2}


def test_qualification_rejects_dirty_or_missing_source_identity():
    assert qualify_package.qualifying_source("a" * 40, "")
    assert not qualify_package.qualifying_source("", "")
    for status in (
        " M src/pydandict/_compat.py",
        "?? tests/new_contract.py",
        " M tools/qualify_package.py",
    ):
        assert not qualify_package.qualifying_source("a" * 40, status)


def test_evidence_inventory_separates_behavior_from_execution_applicability():
    inventory = qualify_package._AC_TEST_LANE_MAP
    assert set(inventory) == {f"AC-{index:03}" for index in range(1, 29)}
    for criterion in inventory.values():
        assert criterion["tests"]
        assert len(criterion["matrix_cells"]) == 11
        for cell in criterion["matrix_cells"].values():
            assert cell["status"] in ("required-external-execution", "non-applicable")
            assert cell["reason"]
    for behavior in qualify_package._BEHAVIOR_MATRIX.values():
        assert behavior["axes"] and behavior["applicable"] and behavior["non_applicable"]
        for criterion in behavior["criteria"]:
            assert set(behavior["tests"]) <= set(inventory[criterion]["tests"])


def test_scalar_mapping_consumers_do_not_invoke_serializers():
    calls = []

    class Record(DictModel):
        model_config = ConfigDict(extra="allow")
        value: int = Field(default=1, alias="input_value")
        hidden: str = Field(default="secret", exclude=True)

        @field_serializer("value")
        def encode(self, value):
            calls.append(value)
            return "encoded"

    record = Record()
    assert all(isinstance(record, kind) for kind in (BaseModel, Mapping, MutableMapping))
    assert record["hidden"] == "secret" and "input_value" not in record
    for key in ("missing", 1):
        with pytest.raises(KeyError):
            record[key]
        assert record.get(key, "fallback") == "fallback" and key not in record
    items, values = record.items(), record.values()
    assert {**record} == dict(record) == {"value": 1, "hidden": "secret"}
    match record:
        case {"value": 1, "hidden": "secret"}:
            pass
        case _:
            pytest.fail("canonical mapping pattern did not match")
    record.value = 2
    record["extra"] = 3
    assert list(items) == [("value", 2), ("hidden", "secret"), ("extra", 3)]
    assert list(values) == [2, "secret", 3] and calls == []
    assert record.model_dump() == {"value": "encoded", "extra": 3} and calls == [2]


def test_scalar_cache_metadata_context_failure_and_noop_transitions():
    events = []

    class Record(DictModel):
        model_config = ConfigDict(extra="allow")
        value: int = Field(default=1, ge=0)
        nullable: int | None = None

        @field_validator("value")
        @classmethod
        def observe(cls, value, info):
            events.append((info.mode, info.context))
            return value

        @computed_field
        @cached_property
        def doubled(self) -> int:
            return self.value * 2

    record = Record.model_validate({"value": 2, "extra": 3}, context={"request": 1})
    assert record.doubled == 4
    old = record.__dict__["doubled"]
    events.clear()
    record.update()
    record.reset()
    record.setdefault("value", object())
    assert record.__dict__["doubled"] is old and events == []
    with pytest.raises(ValidationError):
        record.value = -1
    assert record.__dict__["doubled"] is old and dict(record) == {
        "value": 2,
        "nullable": None,
        "extra": 3,
    }
    record.model_fields_set.clear()
    record.model_extra.clear()
    assert record.model_fields_set == {"value", "extra"} and record["extra"] == 3
    clone = record.model_copy(update={"value": 3})
    assert clone.value == 3 and record.value == 2
    record.value = 4
    assert "doubled" not in record.__dict__ and record.doubled == 8
    record.reset("value")
    record.pop("extra")
    assert record.model_fields_set == set()
    assert record.model_dump(exclude_unset=True) == {"doubled": 2}
    assert record.model_dump(exclude_none=True, exclude_defaults=True) == {"doubled": 2}
    assert events and all(event == ("python", None) for event in events)


def test_scalar_fieldless_rejected_clear_and_typed_extra_reset_errors():
    class RequiredExtra(DictModel):
        model_config = ConfigDict(extra="allow")
        __pydantic_extra__: dict[str, int] = Field(init=False)

        @model_validator(mode="after")
        def require_one(self):
            if not self.model_extra:
                raise ValueError("one extra is required")
            return self

    record = RequiredExtra(a=1)
    assert record.setdefault("b", "2") == 2
    with pytest.raises(ValidationError, match="pydandict_reset_required"):
        record.reset("a")
    with pytest.raises(KeyError):
        record.reset("absent")
    before = (dict(record), record.model_fields_set)
    with pytest.raises(ValidationError, match="one extra is required"):
        record.clear()
    assert (dict(record), record.model_fields_set) == before
    record["a"] = "3"
    assert record["a"] == 3


@pytest.mark.parametrize("frozen", [False, True])
def test_scalar_copy_and_inherited_api_inventory(frozen):
    class Record(DictModel):
        model_config = ConfigDict(frozen=frozen, extra="allow")
        value: int = Field(default=1, ge=0)

    record = Record(value=2, extra=3)
    for copier in (
        copy.copy,
        copy.deepcopy,
        lambda m: m.model_copy(),
        lambda m: m.model_copy(deep=True),
    ):
        clone = copier(record)
        assert type(clone) is Record and clone is not record
        assert dict(clone) == dict(record) and clone.model_fields_set == record.model_fields_set
    with pytest.warns(DeprecationWarning):
        clone = record.copy(update={"value": 4})
    assert clone.value == 4 and record.value == 2
    for options in ({"include": {"value"}}, {"exclude": {"extra"}}):
        with pytest.warns(DeprecationWarning), pytest.raises(TypeError):
            record.copy(**options)
    with pytest.raises(ValidationError):
        record.model_copy(update={"value": -1})
    with pytest.warns(DeprecationWarning):
        assert Record.parse_obj({"value": "3"}).value == 3
    with pytest.warns(DeprecationWarning):
        assert Record.parse_raw('{"value":"3"}').value == 3
    with pytest.warns(DeprecationWarning):
        assert record.dict()["value"] == 2
    with pytest.warns(DeprecationWarning):
        assert '"value":2' in record.json()
    with pytest.warns(DeprecationWarning):
        assert "value" in Record.schema()["properties"]
    with pytest.warns(DeprecationWarning), pytest.raises(TypeError):
        Record.construct(value=2)
    with pytest.raises(TypeError):
        Record.model_construct(value=2)
    with pytest.raises(TypeError):
        pickle.dumps(record)
