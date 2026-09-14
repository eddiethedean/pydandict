"""Regression coverage for native error projection at every public entry."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError, model_validator

from pydandict import DictModel


class Child(DictModel):
    value: int


class Parent(DictModel):
    value: int

    @model_validator(mode="before")
    @classmethod
    def relay(cls, value):
        if value["value"] == 9:
            Child.model_validate_strings({"value": "invalid"})
        return value


@pytest.mark.parametrize(
    "operation",
    [
        lambda: Parent.model_validate({"value": 9}),
        lambda: setattr(Parent(value=1), "value", 9),
        lambda: Parent(value=1).model_copy(update={"value": 9}),
    ],
    ids=["python-validation", "assignment", "copy"],
)
def test_relayed_native_errors_do_not_expose_internal_audit_location(operation):
    with pytest.raises(ValidationError) as raised:
        operation()

    error = raised.value
    assert error.errors()[0]["loc"] == ("value",)
    assert "__pydandict_input_audit_" not in str(error)
    assert "__pydandict_input_audit_" not in repr(error)


def test_existing_pydantic_entries_project_errors_after_late_pydandict_import():
    source = """
from pydantic import BaseModel, TypeAdapter, ValidationError, model_validator

class Envelope(BaseModel):
    value: int
    @model_validator(mode='before')
    @classmethod
    def relay(cls, value):
        Child.model_validate_strings({'value': 'invalid'})
        return value

old_adapter = TypeAdapter(Envelope)
from pydandict import DictModel

class Child(DictModel):
    value: int

for validate in (Envelope.model_validate, old_adapter.validate_python,
                 TypeAdapter(Envelope).validate_python):
    try:
        validate({'value': 1})
    except ValidationError as error:
        assert error.errors()[0]['loc'] == ('value',)
        assert '__pydandict_input_audit_' not in repr(error)
    else:
        raise AssertionError('invalid relayed input was accepted')
"""
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(Path(__file__).parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-c", source],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    assert result.returncode == 0, result.stderr
