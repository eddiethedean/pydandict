"""Native-mode and compiler lifecycle controls for the embedded SOL-017 fix."""

import json
from datetime import date
from typing import Any

import pytest
from pydantic import BaseModel, Field, TypeAdapter, create_model, model_validator

from pydandict import DictModel, _compat


@pytest.mark.parametrize("route", ["model-json", "model-strings", "list-json"])
def test_embedded_entry_preserves_native_strictness(route):
    class Child(DictModel):
        when: date = Field(strict=True)
        count: int

    class ControlChild(BaseModel):
        when: date = Field(strict=True)
        count: int

    class Envelope(BaseModel):
        child: Child

    class ControlEnvelope(BaseModel):
        child: ControlChild

    value = {"when": "2026-01-01", "count": "2"}
    if route == "list-json":
        actual = TypeAdapter(list[Child]).validate_json(json.dumps([value]))
        expected = TypeAdapter(list[ControlChild]).validate_json(json.dumps([value]))
        assert actual[0].model_dump() == expected[0].model_dump()
    else:
        actual, expected = TypeAdapter(Envelope), TypeAdapter(ControlEnvelope)
        payload = {"child": value}
        if route == "model-strings":
            result = actual.validate_strings(payload, strict=True)
            control = expected.validate_strings(payload, strict=True)
        else:
            result = actual.validate_json(json.dumps(payload))
            control = expected.validate_json(json.dumps(payload))
        assert result.model_dump() == control.model_dump()


@pytest.mark.parametrize("mode", ["python", "json", "strings"])
@pytest.mark.parametrize("stage", ["before", "wrap", "after"])
def test_embedded_callbacks_preserve_source_and_mode(mode, stage):
    events = []

    def reject(value, info):
        events.append((info.mode, info.context))
        payload = value.value if isinstance(value, DictModel) else value["value"]
        payload["count"] = "changed"
        raise RuntimeError("callback rejection")

    def before(cls, value, info):
        return reject(value, info)

    def wrap(cls, value, handler, info):
        return reject(handler(value), info)

    def after(self, info):
        return reject(self, info)

    function = {"before": classmethod(before), "wrap": classmethod(wrap), "after": after}[stage]
    Child = create_model(
        "Child",
        __base__=DictModel,
        value=(Any, ...),
        __validators__={"reject": model_validator(mode=stage)(function)},
    )
    Envelope = create_model("Envelope", __base__=BaseModel, child=(Child, ...))
    source = {"child": {"value": {"count": "2"}}}
    payload = json.dumps(source) if mode == "json" else source
    context = {"request": "embedded"}
    with pytest.raises(RuntimeError, match="callback rejection"):
        getattr(TypeAdapter(Envelope), "validate_" + mode)(payload, context=context)
    assert source == {"child": {"value": {"count": "2"}}}
    assert events and all(
        event == ({"python": "python", "json": "json", "strings": "string"}[mode], context)
        for event in events
    )


@pytest.mark.parametrize("failure", [TypeError, KeyboardInterrupt])
def test_rewritten_compilation_restores_completion_flags(monkeypatch, failure):
    class Child(DictModel):
        value: int = Field(alias="input_value")

    class Parent(DictModel):
        child: Child

    original = (Child.__pydantic_complete__, Parent.__pydantic_complete__)
    _compat.compile_validator(_compat.core_schema(Parent))
    assert (Child.__pydantic_complete__, Parent.__pydantic_complete__) == original

    def reject(schema):
        assert not Child.__pydantic_complete__ and not Parent.__pydantic_complete__
        raise failure("compile failure")

    with monkeypatch.context() as patch:
        patch.setattr(_compat, "SchemaValidator", reject)
        with pytest.raises(failure):
            _compat.compile_validator(_compat.core_schema(Parent))
    assert (Child.__pydantic_complete__, Parent.__pydantic_complete__) == original
    record = Parent(child={"input_value": 2})
    record.child.value = "3"
    assert record.child.value == 3
