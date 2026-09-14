# pyright: strict
from collections.abc import (
    ItemsView,
    Iterator,
    KeysView,
    Mapping,
    MutableMapping,
    MutableSequence,
    ValuesView,
)
from typing import assert_type
from pydantic import BaseModel, Field
from pydandict_prototype import DictModel


class Record(DictModel):
    age: int
    labels: MutableSequence[str] = Field(default_factory=list)


record = Record(age=1)
base: BaseModel = record
mapping: Mapping[str, object] = record
mutable: MutableMapping[str, object] = record
assert_type(record.age, int)
assert_type(record.labels, MutableSequence[str])
assert_type(record["age"], object)
assert_type(iter(record), Iterator[str])
assert_type(record.keys(), KeysView[str])
assert_type(record.values(), ValuesView[object])
assert_type(record.items(), ItemsView[str, object])
assert_type(record.model_copy(), Record)
assert_type(record.update(age=2), None)
assert_type(record.setdefault("age", 3), object)
assert_type(record.pop("absent", 3), object)
assert_type(record.get("age"), object | None)
record |= {"age": 2}
assert_type(record, Record)
record["age"] = "3"
