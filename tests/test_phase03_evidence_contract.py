"""Implementation-side proof for the SOL-015 inventory's missing scalar anchors."""

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError

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
