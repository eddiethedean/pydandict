"""Replace a small constrained settings dictionary with a DictModel."""

from collections.abc import Mapping, MutableMapping

from pydantic import ConfigDict, Field, ValidationError, model_validator

from pydandict import DictModel


class LibraryConfig(DictModel):
    """Scalar configuration with an invariant across two fields."""

    model_config = ConfigDict(extra="allow")

    low: int = Field(default=1, ge=0)
    high: int = Field(default=3, ge=0)

    @model_validator(mode="after")
    def ordered(self) -> "LibraryConfig":
        if self.low > self.high:
            raise ValueError("low must not exceed high")
        return self


config = LibraryConfig()
reader: Mapping[str, object] = config
assert reader["low"] == config.low == 1
writer: MutableMapping[str, object] = config
writer["note"] = "library"
assert config.model_fields_set == {"note"}
config.update(low=5, high=8)
assert dict(config) == {"low": 5, "high": 8, "note": "library"}
clone = config.model_copy()
clone["note"] = "copy"
assert config["note"] == "library"

try:
    config.update(low=9, high=4)
except ValidationError:
    assert dict(config) == {"low": 5, "high": 8, "note": "library"}
else:
    raise AssertionError("invalid coupled update was accepted")

config.reset("low", "high")
assert dict(config) == {"low": 1, "high": 3, "note": "library"}
assert config.pop("note") == "library"
assert config.model_fields_set == set()
