"""Reproduce upstream behavior. Does not implement or test Pydandict safety."""

from __future__ import annotations

import json
import platform
from collections.abc import Mapping, MutableMapping
from importlib.metadata import version
from typing import Self

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    TypeAdapter,
    ValidationError,
    computed_field,
    model_validator,
)
from typing_extensions import TypedDict

from probe_typing import MappingProbe


def main() -> None:
    checks: dict[str, object] = {}

    class Plain(BaseModel):
        x: int

    plain = Plain(x=1)
    assert list(plain) == [("x", 1)]
    assert not isinstance(plain, Mapping)
    checks["basemodel_iteration"] = {"pairs": list(plain), "mapping": False}

    class Bounds(BaseModel):
        model_config = ConfigDict(validate_assignment=True)
        low: int
        high: int

        @model_validator(mode="after")
        def ordered(self) -> Self:
            if self.low > self.high:
                raise ValueError("low must not exceed high")
            return self

    bounds = Bounds(low=1, high=3)
    try:
        bounds.low = 5
    except ValidationError:
        pass
    else:
        raise AssertionError("Expected model validator failure")
    assert (bounds.low, bounds.high) == (5, 3)
    checks["failed_after_assignment_retains_value"] = bounds.model_dump()

    class Frozen(BaseModel):
        model_config = ConfigDict(frozen=True)
        values: list[int]

    frozen = Frozen(values=[1])
    frozen.values.append("bad")  # type: ignore[arg-type]
    assert frozen.values[-1] == "bad"
    root = RootModel[dict[str, int]]({"x": 1})
    root.root["x"] = "bad"  # type: ignore[assignment]
    assert root.root["x"] == "bad"
    checks["frozen_and_root_descendants_are_unguarded"] = True

    copied = plain.model_copy(update={"x": "bad"})
    constructed = Plain.model_construct(x="bad")
    assert copied.x == constructed.x == "bad"
    checks["copy_update_and_construct_skip_validation"] = True

    class Defaults(BaseModel):
        x: int = "bad"  # type: ignore[assignment]

    assert Defaults().x == "bad"
    checks["defaults_are_not_validated_by_default"] = True

    class Ignore(BaseModel):
        model_config = ConfigDict(extra="ignore", validate_assignment=True)
        x: int = 1

    ignore = Ignore.model_validate({"extra": 2})
    assert ignore.model_extra is None
    try:
        setattr(ignore, "extra", 2)
    except ValidationError as exc:
        assert exc.errors()[0]["type"] == "no_such_attribute"
    else:
        raise AssertionError("Expected unknown assignment failure")
    checks["ignore_input_vs_assignment"] = "input ignored; assignment rejected"

    class Rich(BaseModel):
        x: int = 1
        hidden: int = Field(default=2, exclude=True)

        @computed_field
        @property
        def doubled(self) -> int:
            return self.x * 2

    rich = Rich()
    assert dict(rich) == {"x": 1, "hidden": 2}
    assert rich.model_dump() == {"x": 1, "doubled": 2}
    assert rich.model_fields_set == set()
    assert Rich.model_validate(dict(rich)).model_fields_set == {"x", "hidden"}
    checks["mapping_serialization_and_fields_set_differ"] = True

    class Record(TypedDict):
        age: int

    record = TypeAdapter(Record).validate_python({"age": "41"})
    assert record["age"] == 41
    record["age"] = "bad"  # type: ignore[typeddict-item]
    assert record["age"] == "bad"
    checks["typeadapter_typeddict_only_validates_at_boundary"] = True

    probe = MappingProbe(x=1)
    assert isinstance(probe, (BaseModel, Mapping))
    assert isinstance(probe, BaseModel) and isinstance(probe, MutableMapping)
    assert list(probe) == ["x"] and dict(probe) == {"x": 1}
    assert probe.model_dump() == {"x": 1}
    assert jsonable_encoder(probe) == {"x": 1}
    assert probe.model_json_schema()["properties"]["x"]["type"] == "integer"
    try:
        json.dumps(probe)
    except TypeError:
        pass
    else:
        raise AssertionError("Built-in JSON encoder unexpectedly accepted model")
    checks["minimal_bridge_reads_and_pydantic_serialization"] = True

    app = FastAPI()

    @app.post("/probe", response_model=MappingProbe)
    def endpoint(body: MappingProbe) -> MappingProbe:
        assert isinstance(body, BaseModel) and isinstance(body, MutableMapping)
        return body

    with TestClient(app) as client:
        response = client.post("/probe", json={"x": "2"})
        assert response.status_code == 200 and response.json() == {"x": 2}
        assert client.post("/probe", json={"x": "bad"}).status_code == 422
        schemas = client.get("/openapi.json").json()["components"]["schemas"]
        assert schemas["MappingProbe"]["properties"]["x"]["type"] == "integer"
    checks["minimal_bridge_fastapi_http_and_openapi"] = True

    print(json.dumps({
        "python": platform.python_version(),
        "versions": {name: version(name) for name in
                     ("pydantic", "fastapi", "httpx", "pyright")},
        "checks": checks,
        "scope": "Upstream observations and incomplete bridge only; no Pydandict implementation",
    }, indent=2))


if __name__ == "__main__":
    main()
