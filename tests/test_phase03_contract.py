"""Focused Phase 0.3 scalar-core contract regressions."""

import pytest
from pydantic import ConfigDict, Field, ValidationError, model_validator

from pydandict import DictModel


class ScalarRecord(DictModel):
    model_config = ConfigDict(extra="allow")

    low: int = Field(default=1, ge=0)
    high: int = Field(default=3, ge=0)

    @model_validator(mode="after")
    def ordered(self):
        if self.low > self.high:
            raise ValueError("low must not exceed high")
        return self


def test_scalar_reads_views_and_canonical_namespace() -> None:
    record = ScalarRecord()

    assert record.low == record["low"] == 1
    assert list(record) == ["low", "high"]
    assert len(record) == 2 and bool(record)
    sentinel = object()
    assert record.get("missing") is None
    assert record.get("missing", sentinel) is sentinel
    assert 1 not in record
    assert record.model_fields_set == set()

    record["note"] = "ready"
    assert list(record) == ["low", "high", "note"]
    assert list(record.keys()) == ["low", "high", "note"]
    assert dict(record)["note"] == "ready"


def test_non_string_pop_is_rejected_before_fallback() -> None:
    record = ScalarRecord()
    before = dict(record)

    with pytest.raises(TypeError, match="pydandict_protected_name"):
        record.pop(1, "fallback")  # type: ignore[arg-type]

    assert dict(record) == before


def test_scalar_bulk_failure_is_atomic_and_reset_updates_metadata() -> None:
    record = ScalarRecord(low=1, high=3)
    record.update(low=2, high=4, note="ok")
    assert (record.low, record.high, record["note"]) == (2, 4, "ok")
    assert record.model_fields_set == {"low", "high", "note"}

    before = (dict(record), record.model_fields_set)
    with pytest.raises(ValidationError):
        record.update(low=9, high=4)
    assert (dict(record), record.model_fields_set) == before

    record.reset("low", "low")
    assert (record.low, record.high) == (1, 4)
    assert record.model_fields_set == {"high", "note"}


def test_scalar_copy_is_validated_and_independent() -> None:
    record = ScalarRecord(low=2, high=4, note="source")
    clone = record.model_copy(update={"low": 3})

    assert clone is not record
    assert clone.low == 3 and record.low == 2
    clone["note"] = "clone"
    assert record["note"] == "source"

    with pytest.raises(ValidationError):
        record.model_copy(update={"low": 8})
    assert record.low == 2
