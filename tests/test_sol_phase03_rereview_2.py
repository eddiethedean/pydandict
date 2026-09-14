"""Independent verification of the remaining Phase 0.3 entry-mode blocker."""

import pytest
from pydantic import BaseModel, TypeAdapter, ValidationError

from pydandict import DictModel


def test_sol017_type_adapter_strict_json_matches_pinned_basemodel():
    class Control(BaseModel):
        value: int

    class Record(DictModel):
        value: int

    payload = '{"value":"2"}'
    with pytest.raises(ValidationError):
        TypeAdapter(Control).validate_json(payload, strict=True)
    with pytest.raises(ValidationError):
        TypeAdapter(Record).validate_json(payload, strict=True)
