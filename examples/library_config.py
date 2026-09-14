"""Replace a small constrained settings dictionary with a DictModel."""

from pydantic import Field, ValidationError, model_validator

from pydandict import DictModel


class LibraryConfig(DictModel):
    """Scalar configuration with an invariant across two fields."""

    low: int = Field(default=1, ge=0)
    high: int = Field(default=3, ge=0)

    @model_validator(mode="after")
    def ordered(self) -> "LibraryConfig":
        if self.low > self.high:
            raise ValueError("low must not exceed high")
        return self


config = LibraryConfig()
assert config["low"] == config.low == 1
config.update(low=5, high=8)
assert dict(config) == {"low": 5, "high": 8}

try:
    config.update(low=9, high=4)
except ValidationError:
    assert dict(config) == {"low": 5, "high": 8}
else:
    raise AssertionError("invalid coupled update was accepted")

config.reset("low", "high")
assert dict(config) == {"low": 1, "high": 3}
