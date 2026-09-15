"""FINAL-006: native error redaction survives audit-path projection."""

import json
from typing import Any

import pytest
from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError, field_validator
from pydantic_core import PydanticCustomError

from pydandict import DictModel

SECRET = "release-secret-9f2b"


def _model(base: type[BaseModel], *, hide_input: bool, failure: str) -> type[BaseModel]:
    namespace: dict[str, Any] = {
        "__annotations__": {"value": int if failure == "parsing" else str},
        "model_config": ConfigDict(hide_input_in_errors=hide_input),
    }
    if failure == "value-error":

        def reject(value):
            raise ValueError("diagnostic contains input_value=marker")

        namespace["check"] = field_validator("value")(reject)
    elif failure == "custom":

        def reject(value):
            raise PydanticCustomError(
                "custom_failure",
                "diagnostic contains input_value={marker}",
                {"marker": "marker"},
            )

        namespace["check"] = field_validator("value")(reject)
    return type("Record", (base,), namespace)


def _capture_error(
    base: type[BaseModel],
    *,
    hide_input: bool,
    failure: str,
    mode: str,
    embedded: bool,
) -> ValidationError:
    record = _model(base, hide_input=hide_input, failure=failure)
    target = record
    value: dict[str, object] = {"value": "not-an-integer" if failure == "parsing" else SECRET}
    if embedded:
        target = type(
            "Envelope",
            (BaseModel,),
            {
                "__annotations__": {"child": record},
                "model_config": ConfigDict(hide_input_in_errors=hide_input),
            },
        )
        value = {"child": value}
    source: object = json.dumps(value) if mode == "json" else value
    with pytest.raises(ValidationError) as raised:
        getattr(TypeAdapter(target), "validate_" + mode)(source)
    return raised.value


@pytest.mark.parametrize("mode", ["python", "json", "strings"])
@pytest.mark.parametrize("embedded", [False, True], ids=["direct", "embedded"])
@pytest.mark.parametrize("failure", ["parsing", "value-error", "custom"])
@pytest.mark.parametrize("hide_input", [False, True], ids=["visible", "hidden"])
def test_native_audit_preserves_hide_input_configuration(mode, embedded, failure, hide_input):
    expected = _capture_error(
        BaseModel,
        hide_input=hide_input,
        failure=failure,
        mode=mode,
        embedded=embedded,
    )
    actual = _capture_error(
        DictModel,
        hide_input=hide_input,
        failure=failure,
        mode=mode,
        embedded=embedded,
    )

    input_value = "not-an-integer" if failure == "parsing" else SECRET
    assert str(actual) == str(expected)
    assert (input_value in str(actual)) is not hide_input
    assert actual.errors(include_context=False) == expected.errors(include_context=False)
    assert json.loads(actual.json()) == json.loads(expected.json())
    assert "__pydandict_input_audit_" not in repr(actual)
