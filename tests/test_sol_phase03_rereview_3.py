"""Independent verification of the remaining Phase 0.3 mode-preservation blocker."""

from datetime import date

from pydantic import BaseModel, Field, TypeAdapter

from pydandict import DictModel


def test_sol017_type_adapter_strict_strings_matches_pinned_basemodel():
    class Control(BaseModel):
        value: int

    class Record(DictModel):
        value: int

    source = {"value": "2"}
    expected = TypeAdapter(Control).validate_strings(source, strict=True)
    actual = TypeAdapter(Record).validate_strings(source, strict=True)
    assert actual.value == expected.value == 2
    assert actual.model_fields_set == expected.model_fields_set == {"value"}
    assert source == {"value": "2"}


def test_sol017_type_adapter_json_preserves_field_specific_strictness():
    class Control(BaseModel):
        date_value: date = Field(strict=True)
        count: int

    class Record(DictModel):
        date_value: date = Field(strict=True)
        count: int

    source = '{"date_value":"2026-01-01","count":"2"}'
    expected = TypeAdapter(Control).validate_json(source)
    actual = TypeAdapter(Record).validate_json(source)
    assert actual.date_value == expected.date_value == date(2026, 1, 1)
    assert actual.count == expected.count == 2
