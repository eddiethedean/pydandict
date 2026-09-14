"""Native entry differential matrix; exclusions live beside the case inventory."""

import json
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from typing import Annotated, Any, Generic, Literal, TypeVar
from uuid import UUID

import pytest
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    create_model,
    model_validator,
)

from pydandict import DictModel

LEAVES = [
    ("none", type(None), None, None),
    ("bool", bool, True, "true"),
    ("int", int, 2, "2"),
    ("float", float, 2.5, "2.5"),
    ("str", str, "ready", "ready"),
    ("bytes", bytes, b"ready", "ready"),
    ("decimal", Decimal, Decimal("2.5"), "2.5"),
    ("date", date, date(2026, 1, 1), "2026-01-01"),
    ("datetime", datetime, datetime(2026, 1, 1), "2026-01-01T00:00:00"),
    ("time", time, time(12), "12:00:00"),
    ("timedelta", timedelta, timedelta(seconds=2), "PT2S"),
    ("uuid", UUID, UUID(int=1), "00000000-0000-0000-0000-000000000001"),
]
# None has no strings-input representation: Pydantic's strings entry accepts
# strings/dicts, not a null value. Python and JSON null are both exercised.
NATIVE_MATRIX_EXCLUSIONS = {
    "none/strings": "Strings input cannot represent a null leaf.",
    "parsed-custom-timezone/all": (
        "The closed envelope excludes Pydantic TzInfo/custom tzinfo; "
        "native datetime.timezone is tested separately."
    ),
}
ENTRY_CASES = [
    (name, annotation, native, text, mode, adapter)
    for name, annotation, native, text in LEAVES
    for mode in ("python", "json", "strings")
    for adapter in (False, True)
    if f"{name}/{mode}" not in NATIVE_MATRIX_EXCLUSIONS
]


def entry(model, mode, adapter, payload, **options):
    target = TypeAdapter(model) if adapter else model
    method = ("validate_" if adapter else "model_validate_") + mode
    if mode == "python" and not adapter:
        method = "model_validate"
    return getattr(target, method)(payload, **options)


def outcome(model, mode, adapter, payload, **options):
    try:
        result = entry(model, mode, adapter, payload, **options)
    except ValidationError as error:
        return "rejected", [(item["loc"], item["type"]) for item in error.errors()]
    return "accepted", (result.model_dump(), result.model_fields_set)


@pytest.mark.parametrize("strict", [None, False, True])
@pytest.mark.parametrize(
    "name,annotation,native,text,mode,adapter",
    ENTRY_CASES,
    ids=[f"{case[0]}-{case[4]}-{'adapter' if case[5] else 'class'}" for case in ENTRY_CASES],
)
def test_native_leaf_entry_matrix(name, annotation, native, text, mode, adapter, strict):
    control = create_model("Control", __base__=BaseModel, value=(annotation, ...))
    record = create_model("Record", __base__=DictModel, value=(annotation, ...))
    payload = {"value": native} if mode == "python" else {"value": text}
    if mode == "json":
        payload = json.dumps(payload)
    assert outcome(record, mode, adapter, payload, strict=strict) == outcome(
        control, mode, adapter, payload, strict=strict
    )
    if mode == "python" and text is not None:
        # Coercing Python input is intentionally also compared under strict=True.
        assert outcome(record, mode, adapter, {"value": text}, strict=strict) == outcome(
            control, mode, adapter, {"value": text}, strict=strict
        )


ANNOTATIONS = [
    ("nullable", int | None, None),
    ("union", int | str, "2"),
    ("literal", Literal["ready", 2, True], "ready"),
    ("annotated", Annotated[int, Field(ge=0)], "2"),
    ("any", Any, "ready"),
    ("object", object, "ready"),
]


@pytest.mark.parametrize("adapter", [False, True], ids=["class", "adapter"])
@pytest.mark.parametrize("mode", ["python", "json", "strings"])
@pytest.mark.parametrize("name,annotation,value", ANNOTATIONS, ids=[a[0] for a in ANNOTATIONS])
def test_annotation_entry_matrix(name, annotation, value, mode, adapter):
    # Nullable strings uses the non-null member; null is tested in the leaf matrix.
    if name == "nullable" and mode == "strings":
        value = "2"
    control = create_model("Control", __base__=BaseModel, value=(annotation, ...))
    record = create_model("Record", __base__=DictModel, value=(annotation, ...))
    payload = {"value": value}
    if mode == "json":
        payload = json.dumps(payload)
    assert outcome(record, mode, adapter, payload) == outcome(control, mode, adapter, payload)


@pytest.mark.parametrize("mode", ["python", "json", "strings"])
@pytest.mark.parametrize("adapter", [False, True], ids=["class", "adapter"])
def test_forward_generic_typed_extra_entry_matrix(mode, adapter):
    variable = TypeVar("variable")

    class Record(DictModel, Generic[variable]):
        model_config = ConfigDict(extra="allow")
        __pydantic_extra__: dict[str, int] = Field(init=False)
        value: variable

    class Control(BaseModel, Generic[variable]):
        model_config = ConfigDict(extra="allow")
        __pydantic_extra__: dict[str, int] = Field(init=False)
        value: variable

    class Deferred(DictModel):
        value: "Later"

    Later = int
    Deferred.model_rebuild(_types_namespace={"Later": Later})
    payload = {"value": "2", "extra": "3"}
    if mode == "json":
        payload = json.dumps(payload)
    assert outcome(Record[int], mode, adapter, payload) == outcome(
        Control[int], mode, adapter, payload
    )
    assert (
        entry(Deferred, mode, adapter, '{"value":"2"}' if mode == "json" else {"value": "2"}).value
        == 2
    )


@pytest.mark.parametrize("mode", ["python", "json", "strings"])
@pytest.mark.parametrize("adapter", [False, True], ids=["class", "adapter"])
@pytest.mark.parametrize("stage", ["before", "wrap", "after"])
def test_native_callback_source_isolation_and_context(mode, adapter, stage):
    seen = []

    def reject(value, info):
        seen.append((info.mode, info.context))
        source = value.value if isinstance(value, DictModel) else value["value"]
        source["count"] = "changed"
        raise RuntimeError("callback rejection")

    def before(cls, value, info):
        return reject(value, info)

    def wrap(cls, value, handler, info):
        return reject(handler(value), info)

    def after(self, info):
        return reject(self, info)

    function = {"before": classmethod(before), "wrap": classmethod(wrap), "after": after}[stage]
    Record = create_model(
        "Record",
        __base__=DictModel,
        value=(Any, ...),
        __validators__={"reject": model_validator(mode=stage)(function)},
    )

    source = {"value": {"count": "2"}}
    payload = json.dumps(source) if mode == "json" else source
    context = {"request": "native matrix"}
    with pytest.raises(RuntimeError, match="callback rejection"):
        entry(Record, mode, adapter, payload, context=context)
    assert source == {"value": {"count": "2"}}
    assert seen == [
        ("python" if mode == "python" else "json" if mode == "json" else "string", context)
    ]


def test_native_timezone_python_envelope():
    for annotation, value in (
        (datetime, datetime(2026, 1, 1, tzinfo=timezone.utc)),
        (time, time(12, tzinfo=timezone(timedelta(hours=2)))),
    ):
        Record = create_model("Record", __base__=DictModel, value=(annotation, ...))
        for adapter in (False, True):
            assert entry(Record, "python", adapter, {"value": value}, strict=True).value == value


@pytest.mark.parametrize("mode", ["python", "json", "strings"])
@pytest.mark.parametrize("adapter", [False, True], ids=["class", "adapter"])
@pytest.mark.parametrize("extra", ["allow", "ignore", "forbid"])
@pytest.mark.parametrize("strict", [None, False, True])
def test_native_alias_extra_strict_option_matrix(mode, adapter, extra, strict):
    control = create_model(
        "Control",
        __base__=BaseModel,
        __config__=ConfigDict(extra="allow"),
        value=(int, Field(alias="input_value")),
        date_value=(date, Field(strict=True)),
    )
    record = create_model(
        "Record",
        __base__=DictModel,
        __config__=ConfigDict(extra="allow"),
        value=(int, Field(alias="input_value")),
        date_value=(date, Field(strict=True)),
    )
    for by_alias, by_name, key in ((True, False, "input_value"), (False, True, "value")):
        payload = {
            key: "2",
            "date_value": date(2026, 1, 1) if mode == "python" else "2026-01-01",
            "extra": "3",
        }
        if mode == "json":
            payload = json.dumps(payload)
        options = dict(strict=strict, extra=extra, by_alias=by_alias, by_name=by_name)
        assert outcome(record, mode, adapter, payload, **options) == outcome(
            control, mode, adapter, payload, **options
        )


@pytest.mark.parametrize("name,annotation,native,text", LEAVES, ids=[a[0] for a in LEAVES])
def test_scalar_leaf_mapping_copy_serialization_matrix(name, annotation, native, text):
    control = create_model(
        "Control",
        __base__=BaseModel,
        value=(annotation, Field(default=native, alias="input_value")),
    )
    record = create_model(
        "Record", __base__=DictModel, value=(annotation, Field(default=native, alias="input_value"))
    )
    model = record()
    expected = control()
    assert dict(model) == {"value": native} and list(model.items()) == [("value", native)]
    assert model.model_dump(by_alias=True) == expected.model_dump(by_alias=True)
    assert model.model_dump_json(by_alias=True) == expected.model_dump_json(by_alias=True)
    assert record.model_json_schema()["properties"] == control.model_json_schema()["properties"]
    model.update(value=native)
    assert model.value == native and model.model_fields_set == {"value"}
    clone = model.model_copy(update={"value": native})
    assert clone is not model and clone.value == native and clone.model_fields_set == {"value"}
    model.reset("value")
    assert model.value == native and model.model_fields_set == set()


def test_deferred_constructor_retains_caller_namespace():
    class Record(DictModel):
        value: "Later"

    Later = int
    assert Record(value="2").value == 2
    assert Later is int


@pytest.mark.parametrize("mode", ["python", "json", "strings"])
@pytest.mark.parametrize("adapter", [False, True], ids=["class", "adapter"])
def test_native_default_factory_cannot_mutate_caller_field(mode, adapter):
    def reject(data):
        data["value"]["count"] = "changed"
        raise RuntimeError("factory rejection")

    Record = create_model(
        "Record",
        __base__=DictModel,
        value=(Any, ...),
        other=(int, Field(default_factory=reject)),
    )
    source = {"value": {"count": "2"}}
    with pytest.raises(RuntimeError, match="factory rejection"):
        entry(Record, mode, adapter, json.dumps(source) if mode == "json" else source)
    assert source == {"value": {"count": "2"}}


@pytest.mark.parametrize("adapter", [False, True], ids=["class", "adapter"])
def test_python_attribute_ingress_retains_closed_source_boundary(adapter):
    class Record(DictModel):
        value: int

    class Attributes:
        value = 2

    with pytest.raises(TypeError, match="pydandict_unsupported_value"):
        entry(Record, "python", adapter, Attributes(), from_attributes=True)
    assert entry(Record, "python", adapter, {"value": "2"}, from_attributes=True).value == 2
