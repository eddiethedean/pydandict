# pyright: strict
from collections.abc import MutableMapping, MutableSequence
from typing import assert_type

from pydandict import DictModel


class Record(DictModel):
    age: int
    labels: MutableSequence[str]


record = Record(age=1, labels=[])
record.age = "bad"  # expected: reportAttributeAccessIssue
record.labels.append(2)  # expected: reportArgumentType
narrow: MutableMapping[str, int] = record  # expected: reportAssignmentType
assert_type(record["age"], int)  # expected: reportAssertTypeFailure
