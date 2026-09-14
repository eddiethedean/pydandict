"""Standalone application using only the wheel's public API."""

from collections.abc import Mapping, MutableMapping, MutableSequence
from pydantic import Field, ValidationError, model_validator
from pydandict_prototype import DictModel


class Config(DictModel):
    low: int = 1
    high: int = 3
    costs: MutableSequence[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def bounded(self):
        if self.low > self.high or sum(self.costs) > self.high:
            raise ValueError("bounds exceeded")
        return self


def consume(record: Mapping[str, object]) -> list[str]:
    return list(record.keys())


def change(record: MutableMapping[str, object]) -> None:
    record.update(low=5, high=8)


def main():
    model = Config()
    assert consume(model) == ["low", "high", "costs"]
    change(model)
    handle = model.costs
    handle.append(2)
    before = model.model_dump_json(), model.model_fields_set
    try:
        handle.append(20)
    except ValidationError:
        pass
    else:
        raise AssertionError("expected parent rejection")
    assert (model.model_dump_json(), model.model_fields_set) == before
    model.reset("low", "high")
    assert model.model_dump(exclude_unset=True) == {"costs": [2]}
    assert model.costs is handle
    print("library consumer: passed")


if __name__ == "__main__":
    main()
