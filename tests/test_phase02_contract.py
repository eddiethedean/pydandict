"""Phase 0.2 contract regressions for annotation and ownership boundaries."""

import copy
from collections.abc import MutableSequence
from datetime import datetime, timedelta, tzinfo
from typing import Any, Generic, TypeVar

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

from pydandict import DictModel


def test_concrete_mutable_annotations_fail_with_migration_hint() -> None:
    with pytest.raises(TypeError, match=r"pydandict_unsupported_annotation:.*MutableSequence"):

        class Concrete(DictModel):
            numbers: list[int]

    with pytest.raises(TypeError, match=r"pydandict_unsupported_annotation:.*MutableSequence"):

        class NestedConcrete(DictModel):
            numbers: tuple[list[int], int]


def test_generic_models_must_be_explicitly_specialized() -> None:
    value_type = TypeVar("value_type")

    class Box(DictModel, Generic[value_type]):
        payload: value_type

    with pytest.raises(TypeError, match="must be explicitly specialized"):
        Box(payload=[1])
    assert Box[MutableSequence[int]](payload=[1]).payload == [1]


def test_custom_timezone_values_are_rejected_without_state_escape() -> None:
    class MutableZone(tzinfo):
        def utcoffset(self, dt: datetime | None) -> timedelta:
            return timedelta(0)

        def dst(self, dt: datetime | None) -> timedelta:
            return timedelta(0)

    class Record(DictModel):
        value: Any

    with pytest.raises(TypeError, match="pydandict_unsupported_value"):
        Record(value=datetime(2026, 1, 1, tzinfo=MutableZone()))


def test_cycles_and_ordinary_base_models_are_rejected() -> None:
    class Ordinary(BaseModel):
        value: int

    class Record(DictModel):
        value: Any

    with pytest.raises(TypeError, match="pydandict_unsupported_value"):
        Record(value=Ordinary(value=1))
    cyclic: list[Any] = []
    cyclic.append(cyclic)
    with pytest.raises(TypeError, match="pydandict_cycle"):
        Record(value=cyclic)


def test_deepcopy_of_a_guard_installs_independent_nested_models() -> None:
    class Child(DictModel):
        value: int

    class Parent(DictModel):
        children: MutableSequence[Child]

    original = Parent(children=[Child(value=1)])
    detached = copy.deepcopy(original.children)
    detached[0].value = 2
    assert detached[0].value == 2
    assert original.children[0].value == 1
    assert detached[0] is not original.children[0]


def test_identity_handle_assignment_checks_frozen_ancestors() -> None:
    class Frozen(DictModel):
        model_config = ConfigDict(frozen=True)
        groups: MutableSequence[MutableSequence[int]]

    model = Frozen(groups=[[1]])
    group = model.groups[0]
    with pytest.raises(ValidationError, match="Frozen ancestor"):
        model.groups[0] = group
    assert model.groups[0] == [1]
