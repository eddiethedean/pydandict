"""Protected Sol re-review contracts for unresolved blockers and a regression."""

from collections.abc import MutableMapping, MutableSequence
from typing import Any, ClassVar, Self

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator
from typing_extensions import TypeAliasType

from pydandict import DictModel


def test_sol001_named_aliases_audit_their_resolved_mutable_type():
    Concrete = TypeAliasType("Concrete", list[int])

    with pytest.raises(TypeError, match=r"^pydandict_unsupported_annotation:.*MutableSequence"):

        class Unsupported(DictModel):
            numbers: Concrete

        Unsupported(numbers=[1])

    Abstract = TypeAliasType("Abstract", MutableSequence[int])

    class Supported(DictModel):
        numbers: Abstract

    model = Supported(numbers=[1])
    model.numbers.append("2")
    assert isinstance(model.numbers, MutableSequence) and model.numbers == [1, 2]


def test_sol001_parent_completion_audits_deferred_nested_fields():
    class Child(DictModel):
        numbers: "Later"

    Later = list[int]

    with pytest.raises(TypeError, match=r"^pydandict_unsupported_annotation:.*MutableSequence"):

        class Parent(DictModel):
            child: Child

        Parent(child={"numbers": [1]})


def test_sol001_parent_completion_audits_deferred_nested_extras():
    class Child(DictModel):
        model_config = ConfigDict(extra="allow")
        __pydantic_extra__: dict[str, "Later"] = Field(init=False)

    Later = list[int]

    with pytest.raises(TypeError, match=r"^pydandict_unsupported_annotation:.*MutableSequence"):

        class Parent(DictModel):
            child: Child

        Parent(child={"extra": [1]})


@pytest.mark.parametrize("operation", ["setdefault", "update_pairs"])
def test_sol002_every_key_insertion_rejects_models_before_native_hashing(operation):
    class Key(DictModel):
        number: int

    class Record(DictModel):
        table: MutableMapping[Any, int]

    model = Record(table={"a": 1})
    handle = model.table
    before = model.model_dump(), model.model_fields_set
    iterator = iter(handle)
    key = Key(number=1)

    with pytest.raises(TypeError, match=r"^pydandict_unsupported_value:"):
        if operation == "setdefault":
            handle.setdefault(key, 2)
        else:
            handle.update([(key, 2)])

    assert (model.model_dump(), model.model_fields_set) == before
    assert model.table is handle
    assert next(iterator) == "a"
    handle["b"] = 2
    assert model.table == {"a": 1, "b": 2}


@pytest.mark.parametrize("operation", ["slice", "mapping_update"])
def test_sol010_input_callbacks_run_under_the_same_root_guard(operation):
    class Record(DictModel):
        marker: int = 0
        numbers: MutableSequence[int]
        table: MutableMapping[str, int]

    model = Record(numbers=[1], table={"a": 1})
    numbers, table = model.numbers, model.table
    before = model.model_dump(), model.model_fields_set
    iterator = iter(numbers)

    def incoming():
        assert model.marker == 0  # Reads must observe committed state.
        model.marker = 9
        yield 2 if operation == "slice" else ("b", 2)
        raise ValueError("late input failure")

    with pytest.raises(RuntimeError, match=r"^pydandict_reentrant_transaction:"):
        if operation == "slice":
            numbers[:] = incoming()
        else:
            table.update(incoming())

    assert (model.model_dump(), model.model_fields_set) == before
    assert model.numbers is numbers and model.table is table
    assert next(iterator) == 1
    model.marker = 2
    assert model.marker == 2


def test_sol012_existing_model_public_validation_preserves_supplied_context():
    class Control(BaseModel):
        model_config = ConfigDict(revalidate_instances="always")
        number: int
        observed: ClassVar[list[object]] = []

        @model_validator(mode="after")
        def observe(self, info: ValidationInfo) -> Self:
            self.observed.append(info.context)
            return self

    class Record(DictModel):
        number: int
        observed: ClassVar[list[object]] = []

        @model_validator(mode="after")
        def observe(self, info: ValidationInfo) -> Self:
            self.observed.append(info.context)
            return self

    context = {"request": 2}
    for cls in (Control, Record):
        cls.model_validate({"number": 1}, context=context)
        assert cls.observed == [context]
        cls.observed.clear()

    control, record = Control(number=1), Record(number=1)
    Control.observed.clear()
    Record.observed.clear()
    Control.model_validate(control, context=context)
    validated = Record.model_validate(record, context=context)
    assert Control.observed == [context]
    assert Record.observed == Control.observed
    assert validated.number == 1

    # Public validation must not retain request context for later transactions/copies.
    Record.observed.clear()
    validated.number = 2
    assert Record.observed == [None]
    Record.observed.clear()
    copied = validated.model_copy()
    assert copied.number == 2 and Record.observed == [None]
