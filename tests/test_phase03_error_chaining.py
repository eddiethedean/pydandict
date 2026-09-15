"""Regression coverage for native exception chaining at the audit boundary."""

import json
from collections.abc import Iterator
from typing import Any

import pytest
from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError, field_validator

from pydandict import DictModel


def _reject(value: int) -> int:
    raise ValueError("boom")


def _exception_description(error: BaseException | None) -> object:
    if error is None:
        return None
    if isinstance(error, BaseExceptionGroup):
        return (
            type(error),
            str(error),
            tuple(_exception_description(child) for child in error.exceptions),
        )
    return type(error), str(error)


def _exception_graph(error: BaseException | None) -> Iterator[BaseException]:
    seen: set[int] = set()
    pending = [error]
    while pending:
        current = pending.pop()
        if current is None or id(current) in seen:
            continue
        seen.add(id(current))
        yield current
        pending.extend((current.__cause__, current.__context__))
        if isinstance(current, BaseExceptionGroup):
            pending.extend(current.exceptions)


def _model(base: type[BaseModel], *, error_cause: bool, validator_failure: bool):
    namespace: dict[str, Any] = {
        "__annotations__": {"value": int},
        "model_config": ConfigDict(validation_error_cause=error_cause),
    }
    if validator_failure:
        namespace["check"] = field_validator("value")(_reject)
    return type("Record", (base,), namespace)


def _capture_error(
    base: type[BaseModel],
    *,
    mode: str,
    embedded: bool,
    error_cause: bool,
    validator_failure: bool,
) -> ValidationError:
    record = _model(base, error_cause=error_cause, validator_failure=validator_failure)
    target = record
    value: dict[str, object] = {"value": "2" if validator_failure else "invalid"}
    if embedded:
        target = type(
            "Envelope",
            (BaseModel,),
            {
                "__annotations__": {"child": record},
                "model_config": ConfigDict(validation_error_cause=error_cause),
            },
        )
        value = {"child": value}
    source: object = json.dumps(value) if mode == "json" else value
    with pytest.raises(ValidationError) as raised:
        getattr(TypeAdapter(target), "validate_" + mode)(source)
    return raised.value


@pytest.mark.parametrize("mode", ["python", "json", "strings"])
@pytest.mark.parametrize("embedded", [False, True], ids=["direct", "embedded"])
@pytest.mark.parametrize("error_cause", [False, True], ids=["cause-off", "cause-on"])
@pytest.mark.parametrize("validator_failure", [False, True], ids=["parsing", "validator"])
def test_native_audit_preserves_exception_chain(mode, embedded, error_cause, validator_failure):
    expected = _capture_error(
        BaseModel,
        mode=mode,
        embedded=embedded,
        error_cause=error_cause,
        validator_failure=validator_failure,
    )
    actual = _capture_error(
        DictModel,
        mode=mode,
        embedded=embedded,
        error_cause=error_cause,
        validator_failure=validator_failure,
    )

    assert actual.errors(include_url=False, include_context=False) == expected.errors(
        include_url=False, include_context=False
    )
    assert json.loads(actual.json(include_url=False)) == json.loads(
        expected.json(include_url=False)
    )
    assert _exception_description(actual.__cause__) == _exception_description(expected.__cause__)
    assert _exception_description(actual.__context__) == _exception_description(
        expected.__context__
    )
    assert actual.__suppress_context__ is expected.__suppress_context__
    assert all("__pydandict_input_audit_" not in repr(item) for item in _exception_graph(actual))


def test_native_audit_does_not_acquire_an_active_caller_exception():
    errors = []
    for base in (BaseModel, DictModel):
        record = _model(base, error_cause=False, validator_failure=False)
        try:
            raise RuntimeError("caller failure")
        except RuntimeError:
            with pytest.raises(ValidationError) as raised:
                record.model_validate_strings({"value": "invalid"})
        errors.append(raised.value)

    expected, actual = errors
    assert actual.__cause__ is expected.__cause__ is None
    assert actual.__context__ is expected.__context__ is None
    assert actual.__suppress_context__ is expected.__suppress_context__ is False
