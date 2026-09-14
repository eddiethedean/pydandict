"""SOL-001 audits completed extra annotations rather than raw annotation strings."""

from typing import Generic, TypeVar

import pytest
from pydantic import ConfigDict, Field

from pydandict import DictModel


def test_future_typed_extra_concrete_values_are_rejected():
    namespace = {
        "DictModel": DictModel,
        "ConfigDict": ConfigDict,
        "Field": Field,
        "__name__": __name__,
    }
    with pytest.raises(TypeError, match=r"^pydandict_unsupported_annotation:.*MutableSequence"):
        exec(
            "from __future__ import annotations\n"
            "class Record(DictModel):\n"
            "    model_config = ConfigDict(extra='allow')\n"
            "    __pydantic_extra__: dict[str, list[int]] = Field(init=False)\n",
            namespace,
        )


def test_deferred_extra_completion_audits_the_resolved_value():
    class Record(DictModel):
        model_config = ConfigDict(extra="allow")
        __pydantic_extra__: dict[str, "Later"] = Field(init=False)

    Later = list[int]
    with pytest.raises(TypeError, match=r"^pydandict_unsupported_annotation:.*MutableSequence"):
        Record.model_rebuild(_types_namespace={"Later": Later})


def test_specialized_extra_type_variables_are_audited():
    T = TypeVar("T")

    class Record(DictModel, Generic[T]):
        model_config = ConfigDict(extra="allow")
        __pydantic_extra__: dict[str, T] = Field(init=False)

    with pytest.raises(TypeError, match=r"^pydandict_unsupported_annotation:.*MutableSequence"):
        Record[list[int]](extra=[1])
    assert Record[int](extra=1)["extra"] == 1


def test_inherited_extra_model_annotations_require_specialization():
    T = TypeVar("T")

    class Box(DictModel, Generic[T]):
        value: T

    class Parent(DictModel):
        model_config = ConfigDict(extra="allow")
        __pydantic_extra__: dict[str, Box] = Field(init=False)

    class Child(Parent):
        pass

    with pytest.raises(TypeError, match=r"^pydandict_unsupported_annotation:"):
        Child(extra={"value": [1]})
