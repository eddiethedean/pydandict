"""Scalar roles, extra policies and freezing with observable atomic outcomes."""

import operator

import pytest
from pydantic import ConfigDict, Field, ValidationError, create_model

from pydandict import DictModel


@pytest.mark.parametrize("policy", ["allow", "ignore", "forbid"])
@pytest.mark.parametrize("freeze", ["mutable", "model", "field"])
@pytest.mark.parametrize("role", ["required", "defaulted", "nullable"])
def test_scalar_role_policy_freeze_matrix(policy, freeze, role):
    annotation = int | None if role == "nullable" else int
    default = ... if role == "required" else None if role == "nullable" else 1
    Record = create_model(
        "Record",
        __base__=DictModel,
        __config__=ConfigDict(extra=policy, frozen=freeze == "model"),
        value=(annotation, Field(default=default, frozen=freeze == "field")),
    )
    actions = {
        "setitem": lambda m: operator.setitem(m, "value", "3"),
        "attribute": lambda m: setattr(m, "value", "3"),
        "update": lambda m: m.update([("value", 7), ("value", "2")], value="3"),
        "ior": lambda m: operator.ior(m, {"value": "3"}),
        "delete": lambda m: operator.delitem(m, "value"),
        "pop": lambda m: m.pop("value", 9),
        "popitem": lambda m: m.popitem(),
        "clear": lambda m: m.clear(),
        "reset": lambda m: m.reset("value", "value"),
    }
    for name, action in actions.items():
        model = Record(value=2)
        before = (dict(model), list(model), model.model_fields_set, model.model_extra)
        rejected = (
            freeze != "mutable"
            or name in ("delete", "pop", "popitem", "clear")
            or name == "reset"
            and role == "required"
        )
        if rejected:
            with pytest.raises(ValidationError):
                action(model)
            assert (dict(model), list(model), model.model_fields_set, model.model_extra) == before
        else:
            result = action(model)
            assert result is (model if name == "ior" else None)
            assert model.value == (default if name == "reset" else 3)
            assert model.model_fields_set == (set() if name == "reset" else {"value"})
        # Existing setdefault and genuinely empty batches remain no-ops even frozen.
        snapshot = (dict(model), model.model_fields_set)
        assert model.setdefault("value", "bad") == model.value
        assert model.update() is None and model.reset() is None
        assert (dict(model), model.model_fields_set) == snapshot
        if freeze != "mutable":
            with pytest.raises(ValidationError):
                model["value"] = model.value
            with pytest.raises(ValidationError):
                model.update(value=model.value, extra=3)
            assert (dict(model), model.model_fields_set) == snapshot


@pytest.mark.parametrize("policy", ["allow", "ignore", "forbid"])
@pytest.mark.parametrize("frozen", [False, True])
def test_scalar_extra_insertion_missing_and_removal_matrix(policy, frozen):
    class Record(DictModel):
        model_config = ConfigDict(extra=policy, frozen=frozen)
        value: int = 1

    model = Record()
    before = (dict(model), model.model_fields_set, model.model_extra)
    if policy != "allow" or frozen:
        with pytest.raises(ValidationError):
            model.setdefault("extra", 2)
        assert (dict(model), model.model_fields_set, model.model_extra) == before
    else:
        assert model.setdefault("extra", 2) == 2
        assert model.popitem() == ("extra", 2)
        model["extra"] = 3
        del model["extra"]
        assert dict(model) == {"value": 1} and model.model_fields_set == set()
    assert model.pop("absent", 7) == 7
    with pytest.raises(KeyError):
        model.pop("absent")


def test_scalar_empty_clear_validates_and_factory_reset_is_ordered():
    events = []

    class Empty(DictModel):
        model_config = ConfigDict(extra="allow")

    empty = Empty(a=1, b=2)
    assert empty.clear() is None and dict(empty) == {} and empty.model_fields_set == set()
    assert empty.clear() is None

    class Defaults(DictModel):
        first: int = Field(default_factory=lambda: events.append("first") or 2)
        second: int = Field(
            default_factory=lambda data: events.append("second") or data["first"] * 2
        )

    model = Defaults(first=3, second=9)
    model.reset("second", "first", "second")
    assert events == ["first", "second"]
    assert dict(model) == {"first": 2, "second": 4} and model.model_fields_set == set()


def test_scalar_malformed_batches_and_late_iterator_failure_are_atomic():
    class Record(DictModel):
        value: int = 1

    model = Record()
    for malformed, exception in (([("value",)], ValueError), ([1], TypeError)):
        with pytest.raises(exception):
            model.update(malformed)
        assert model.value == 1 and model.model_fields_set == set()

    def failing():
        yield "value", 3
        raise RuntimeError("late failure")

    with pytest.raises(RuntimeError, match="late failure"):
        model.update(failing())
    assert model.value == 1 and model.model_fields_set == set()
    model.value = 2
    assert model.value == 2
