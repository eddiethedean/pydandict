"""SOL-017 / FINAL-001: audit original strings input before scalar coercion."""

import json
from datetime import date
from enum import Enum

import pytest
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticCustomError, SchemaValidator

from pydandict import DictModel


class CustomText(str):
    pass


class TextEnum(str, Enum):
    TWO = "2"


@pytest.mark.parametrize("route", ["class", "adapter", "embedded"])
@pytest.mark.parametrize(
    "unsupported", [CustomText("2"), TextEnum.TWO], ids=["string-subclass", "string-enum"]
)
def test_sol017_strings_coercion_rejects_original_unsupported_input(route, unsupported):
    class Record(DictModel):
        value: int

    class Envelope(BaseModel):
        child: Record

    with pytest.raises(TypeError, match="^pydandict_unsupported_value:"):
        Record.model_validate({"value": unsupported})

    for strict in (None, False, True):
        if route == "embedded":
            validate = TypeAdapter(Envelope).validate_strings
            supported = {"child": {"value": "2"}}
            source = {"child": {"value": unsupported}}
            assert validate(supported, strict=strict).child.value == 2
        else:
            validate = (
                Record.model_validate_strings
                if route == "class"
                else TypeAdapter(Record).validate_strings
            )
            supported = {"value": "2"}
            source = {"value": unsupported}
            assert validate(supported, strict=strict).value == 2

        with pytest.raises(TypeError, match="^pydandict_unsupported_value:"):
            validate(source, strict=strict)


def test_strings_audit_preserves_parent_callback_state_and_native_field_strictness():
    seen = []

    class Child(DictModel):
        value: int
        when: date = Field(strict=True)

        @model_validator(mode="after")
        def observe(self, info):
            seen.append((info.mode, info.field_name, dict(info.data), info.context))
            return self

    class Envelope(BaseModel):
        earlier: int
        child: Child

    context = {"request": 1}
    result = TypeAdapter(Envelope).validate_strings(
        {"earlier": "1", "child": {"value": "2", "when": "2026-01-01"}},
        strict=True,
        context=context,
    )
    assert result.child.when == date(2026, 1, 1)
    assert seen == [("string", "child", {"earlier": 1}, context)]


@pytest.mark.parametrize("mode", ["python", "json", "strings"])
@pytest.mark.parametrize("failure", ["parsing", "custom", "value-error"])
def test_native_audit_preserves_all_public_error_projections(mode, failure):
    def reject(value):
        if failure == "custom":
            raise PydanticCustomError("custom_failure", "bad {value}", {"value": "{value}"})
        if failure == "value-error":
            raise ValueError("bad value")
        return value

    class Child(DictModel):
        model_config = ConfigDict(hide_input_in_errors=True)
        value: int
        check = field_validator("value")(reject)

    class ControlChild(BaseModel):
        model_config = ConfigDict(hide_input_in_errors=True)
        value: int
        check = field_validator("value")(reject)

    class Envelope(BaseModel):
        model_config = ConfigDict(hide_input_in_errors=True)
        child: Child

    class ControlEnvelope(BaseModel):
        model_config = ConfigDict(hide_input_in_errors=True)
        child: ControlChild

    source = {"child": {"value": "invalid" if failure == "parsing" else "2"}}
    if mode == "json":
        source = json.dumps(source)
    errors = []
    for cls in (Envelope, ControlEnvelope):
        with pytest.raises(ValidationError) as raised:
            getattr(TypeAdapter(cls), "validate_" + mode)(source)
        errors.append(raised.value)

    actual, expected = errors
    # ValueError instances differ, but the complete native JSON projection
    # serializes their context identically, without weakening error assertions.
    assert json.loads(actual.json()) == json.loads(expected.json())
    assert actual.error_count() == expected.error_count() == 1
    assert actual.errors(include_context=False) == expected.errors(include_context=False)
    assert actual.json(include_input=False, include_context=False, indent=2) == expected.json(
        include_input=False, include_context=False, indent=2
    )
    assert str(actual).replace("Envelope", "ControlEnvelope") == str(expected)
    assert "__pydandict_input_audit_" not in repr(actual)


def test_native_error_relay_retains_real_line_errors_under_an_ordinary_callback():
    class Child(DictModel):
        value: int

    class Envelope(BaseModel):
        value: int

        @model_validator(mode="before")
        @classmethod
        def relay(cls, value):
            return Child.model_validate_strings({"value": "invalid"})

    with pytest.raises(ValidationError) as raised:
        Envelope.model_validate({"value": 1})
    error = raised.value
    assert error.error_count() == 1
    assert error.errors()[0]["loc"] == ("value",)
    assert error.errors()[0]["type"] == "int_parsing"
    assert "__pydandict_input_audit_" not in str(error)


def test_plain_pydantic_fields_do_not_acquire_the_closed_value_policy():
    class Plain(BaseModel):
        value: int

    class Child(DictModel):
        value: int

    class Envelope(BaseModel):
        unrelated: int
        child: Child

    assert isinstance(Plain.__pydantic_validator__, SchemaValidator)
    assert TypeAdapter(Plain).validate_strings({"value": CustomText("2")}).value == 2
    assert (
        TypeAdapter(Envelope)
        .validate_strings({"unrelated": CustomText("1"), "child": {"value": "2"}})
        .unrelated
        == 1
    )


def test_native_error_locations_with_backslashes_are_formatted_literally():
    class Child(DictModel):
        value: int = Field(alias=r"input\1")

    with pytest.raises(ValidationError) as raised:
        Child.model_validate_strings({r"input\1": "invalid"})
    assert raised.value.errors()[0]["loc"] == (r"input\1",)
    assert "\ninput\\1\n" in str(raised.value)
    assert "__pydandict_input_audit_" not in str(raised.value)
