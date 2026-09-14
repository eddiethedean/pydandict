"""Executable ordinary-method inventory and cross-feature regressions."""

import operator
from functools import cached_property
from typing import Annotated, Generic, Literal, TypeVar

import pytest
from pydantic import (
    AliasChoices,
    AliasPath,
    ConfigDict,
    Field,
    ValidationError,
    computed_field,
    field_validator,
)
from pydandict_prototype import DictModel


class Lists(DictModel):
    nums: list[int] = Field(
        default_factory=lambda: [3, 1, 2], min_length=1, max_length=8
    )


LIST_MUTATIONS = [
    ("set", lambda x: operator.setitem(x, 0, "4"), [4, 1, 2]),
    ("slice", lambda x: operator.setitem(x, slice(0, 2), iter([4, 5])), [4, 5, 2]),
    ("del", lambda x: operator.delitem(x, 0), [1, 2]),
    ("delslice", lambda x: operator.delitem(x, slice(0, 2)), [2]),
    ("append", lambda x: x.append(4), [3, 1, 2, 4]),
    ("extend", lambda x: x.extend(iter([4, 5])), [3, 1, 2, 4, 5]),
    ("insert", lambda x: x.insert(1, 4), [3, 4, 1, 2]),
    ("pop", lambda x: x.pop(), [3, 1]),
    ("remove", lambda x: x.remove(1), [3, 2]),
    ("reverse", lambda x: x.reverse(), [2, 1, 3]),
    ("sort", lambda x: x.sort(), [1, 2, 3]),
    ("iadd", lambda x: operator.iadd(x, [4]), [3, 1, 2, 4]),
    ("imul", lambda x: operator.imul(x, 2), [3, 1, 2, 3, 1, 2]),
]


@pytest.mark.parametrize(
    "name,action,expected", LIST_MUTATIONS, ids=[row[0] for row in LIST_MUTATIONS]
)
def test_list_mutation_inventory(name, action, expected):
    m = Lists()
    h = m.nums
    action(h)
    assert h is m.nums and h == expected
    assert m.model_dump() == {"nums": expected}


@pytest.mark.parametrize(
    "action",
    [
        lambda x: x.clear(),
        lambda x: x.append("bad"),
        lambda x: operator.imul(x, 0),
        lambda x: operator.setitem(x, slice(None), []),
        lambda x: x.extend([1] * 20),
    ],
)
def test_list_failure_inventory(action):
    m = Lists()
    h = m.nums
    with pytest.raises(ValidationError):
        action(h)
    assert h == [3, 1, 2]
    h.append(4)
    assert h == [3, 1, 2, 4]


def test_list_read_inventory():
    h = Lists().nums
    assert len(h) == 3 and bool(h) and str(h) == repr(h) == "[3, 1, 2]"
    assert list(h) == [3, 1, 2] and list(reversed(h)) == [2, 1, 3]
    assert h[1:] == [1, 2] and 1 in h and h.count(1) == 1 and h.index(2) == 2
    assert h.copy() == [3, 1, 2] and h + [4] == [3, 1, 2, 4]
    assert [0] + h == [0, 3, 1, 2] and h * 2 == 2 * h == [3, 1, 2] * 2
    assert h == [3, 1, 2] and [3, 1, 2] == h and h != [1]
    assert h < [4] and h <= [3, 1, 2] and h > [2] and h >= [3, 1, 2]


class Dicts(DictModel):
    table: dict[str, int] = Field(default_factory=lambda: {"a": 1, "b": 2})


DICT_MUTATIONS = [
    ("set", lambda x: operator.setitem(x, "a", "3"), {"a": 3, "b": 2}),
    ("del", lambda x: operator.delitem(x, "a"), {"b": 2}),
    ("update", lambda x: x.update([("a", 3)], c=4), {"a": 3, "b": 2, "c": 4}),
    ("setdefault", lambda x: x.setdefault("c", "3"), {"a": 1, "b": 2, "c": 3}),
    ("pop", lambda x: x.pop("a"), {"b": 2}),
    ("popitem", lambda x: x.popitem(), {"a": 1}),
    ("clear", lambda x: x.clear(), {}),
    ("ior", lambda x: operator.ior(x, {"c": 3}), {"a": 1, "b": 2, "c": 3}),
]


@pytest.mark.parametrize(
    "name,action,expected", DICT_MUTATIONS, ids=[row[0] for row in DICT_MUTATIONS]
)
def test_dict_mutation_inventory(name, action, expected):
    m = Dicts()
    h = m.table
    action(h)
    assert h is m.table and h == expected and m.model_dump() == {"table": expected}


def test_dict_reads_views_and_rejected_update():
    h = Dicts().table
    items = h.items()
    assert dict(h) == {"a": 1, "b": 2} and {**h} == {"a": 1, "b": 2}
    assert list(h.keys()) == ["a", "b"] and list(h.values()) == [1, 2]
    assert h.get("none", 4) == 4 and h.copy() == dict(h)
    assert h | {"c": 3} == {"a": 1, "b": 2, "c": 3}
    assert {"c": 3} | h == {"a": 1, "b": 2, "c": 3}
    with pytest.raises(ValidationError):
        h.update(a=4, c="bad")
    assert h == {"a": 1, "b": 2}
    h["c"] = 3
    assert list(items)[-1] == ("c", 3)
    assert list(reversed(h)) == ["c", "b", "a"]


class Sets(DictModel):
    flags: set[int] = Field(default_factory=lambda: {1, 2})


SET_MUTATIONS = [
    ("add", lambda x: x.add("3"), {1, 2, 3}),
    ("discard", lambda x: x.discard(1), {2}),
    ("remove", lambda x: x.remove(1), {2}),
    ("clear", lambda x: x.clear(), set()),
    ("update", lambda x: x.update([3], [4]), {1, 2, 3, 4}),
    ("intersection_update", lambda x: x.intersection_update({2, 3}), {2}),
    ("difference_update", lambda x: x.difference_update({2, 3}), {1}),
    (
        "symmetric_difference_update",
        lambda x: x.symmetric_difference_update({2, 3}),
        {1, 3},
    ),
    ("ior", lambda x: operator.ior(x, {2, 3}), {1, 2, 3}),
    ("iand", lambda x: operator.iand(x, {2, 3}), {2}),
    ("isub", lambda x: operator.isub(x, {2, 3}), {1}),
    ("ixor", lambda x: operator.ixor(x, {2, 3}), {1, 3}),
]


@pytest.mark.parametrize(
    "name,action,expected", SET_MUTATIONS, ids=[row[0] for row in SET_MUTATIONS]
)
def test_set_mutation_inventory(name, action, expected):
    m = Sets()
    h = m.flags
    action(h)
    assert h is m.flags and h == expected and m.model_dump() == {"flags": expected}


def test_set_read_inventory_and_pop():
    h = Sets().flags
    assert h.copy() == {1, 2} and set(h) == {1, 2} and 1 in h
    assert h.union({3}) == h | {3} == {3} | h == {1, 2, 3}
    assert h.intersection({2, 3}) == h & {2, 3} == {2, 3} & h == {2}
    assert h.difference({2, 3}) == h - {2, 3} == {1}
    assert {2, 3} - h == {3}
    assert h.symmetric_difference({2, 3}) == h ^ {2, 3} == {2, 3} ^ h == {1, 3}
    assert h.isdisjoint({3}) and h.issubset({1, 2, 3}) and h.issuperset({1})
    assert h < {1, 2, 3} and h <= {1, 2} and h > {1} and h >= {1, 2}
    with pytest.raises(ValidationError):
        h.add("bad")
    old = set(h)
    removed = h.pop()
    assert h == old - {removed}


def test_mutable_repetition_tuple_descendants_and_alias_isolation():
    class Nested(DictModel):
        rows: list[list[int]]
        pair: tuple[list[int], int]

    shared = [1]
    m = Nested(rows=[shared, shared], pair=(shared, 1))
    assert m.rows[0] is not m.rows[1] and m.pair[0] is not m.rows[0]
    first = m.rows[0]
    m.rows *= 2
    assert m.rows[0] is first and m.rows[2] is not first
    m.rows[2].append(3)
    assert first == [1]
    m.pair[0].append("2")
    assert m.pair[0] == [1, 2]


def test_cached_computed_fields_are_invalidated():
    class Cached(DictModel):
        x: int

        @computed_field
        @cached_property
        def twice(self) -> int:
            return self.x * 2

    m = Cached(x=2)
    assert m.twice == 4
    m.x = 3
    assert m.twice == 6 and m.model_dump()["twice"] == 6


def test_generic_union_and_recursive_schema():
    T = TypeVar("T")

    class Box(DictModel, Generic[T]):
        payload: T

    box = Box[list[int]](payload=[1])
    box.payload.append("2")
    assert box.payload == [1, 2]

    class A(DictModel):
        kind: Literal["a"] = "a"
        x: int

    class B(DictModel):
        kind: Literal["b"] = "b"
        y: str

    class UnionModel(DictModel):
        item: Annotated[A | B, Field(discriminator="kind")]

    m = UnionModel(item=A(x=1))
    old = m.item
    m.item = {"kind": "b", "y": "ok"}
    assert isinstance(m.item, B)
    with pytest.raises(RuntimeError):
        old.x

    class Node(DictModel):
        value: int
        children: list["Node"] = Field(default_factory=list)

    Node.model_rebuild()
    tree = Node(value=1, children=[{"value": 2}])
    tree.children[0].value = "3"
    assert tree.children[0].value == 3
    assert "$defs" in Node.model_json_schema()
    assert tree.model_dump()["children"][0]["value"] == 3


def test_nested_aliases_and_data_dependent_reset():
    class Aliased(DictModel):
        n: int = Field(alias="number")

    class Outer(DictModel):
        child: Aliased

    m = Outer(child=Aliased(number=1))
    m.child.n = "2"
    assert m.child.n == 2 and m.model_dump(by_alias=True) == {"child": {"number": 2}}

    class Defaults(DictModel):
        a: int = 2
        b: int = Field(default_factory=lambda data: data["a"] * 2)

    m = Defaults()
    m.a = 3
    assert m.b == 4
    m.reset("b")
    assert m.b == 6 and m.model_fields_set == {"a"}


def test_sort_callback_failure_and_programming_error():
    m = Lists()

    def key(value):
        m.nums.append(1)
        return value

    with pytest.raises(RuntimeError, match="reentrant"):
        m.nums.sort(key=key)
    assert m.nums == [3, 1, 2]

    class Broken(DictModel):
        x: int

        @field_validator("x")
        @classmethod
        def programming_error(cls, v):
            if v == 2:
                raise TypeError("programming error")
            return v

    b = Broken(x=1)
    with pytest.raises(TypeError, match="programming error"):
        b.x = 2
    assert b.x == 1
    b.x = 3
    assert b.x == 3


def test_stale_child_repr_equality_and_metadata():
    class Child(DictModel):
        x: int

    class Parent(DictModel):
        child: Child

    m = Parent(child=Child(x=1))
    old = m.child
    m.child = Child(x=2)
    for read in [
        lambda: repr(old),
        lambda: str(old),
        lambda: old == m.child,
        lambda: old.model_fields_set,
        lambda: "x" in old,
    ]:
        with pytest.raises(RuntimeError, match="stale"):
            read()


def test_validated_copy_rejects_unknown_keys_and_drift():
    m = Lists()
    with pytest.raises(ValidationError):
        m.model_copy(update={"typo": 1})

    class Doubler(DictModel):
        x: int

        @field_validator("x")
        @classmethod
        def double(cls, value):
            return value * 2

    m = Doubler(x=2)
    with pytest.raises(TypeError, match="untouched"):
        m.model_copy()
    assert m.x == 4


def test_alias_choices_paths_typed_extras_and_properties():
    class Choice(DictModel):
        n: int = Field(
            validation_alias=AliasChoices("number", AliasPath("nested", "n"))
        )

    for m in [Choice(number=1), Choice.model_validate({"nested": {"n": 1}})]:
        m.n = "2"
        assert m.n == 2

    class TypedExtras(DictModel):
        model_config = ConfigDict(extra="allow")
        __pydantic_extra__: dict[str, int] = Field(init=False)

    m = TypedExtras(a="1")
    assert m["a"] == 1
    assert m.setdefault("b", "2") == 2
    before = m.model_dump()
    with pytest.raises(ValidationError):
        m["a"] = "bad"
    assert m.model_dump() == before


def test_shape_changing_validator_rejected_and_factory_failure_recovers():
    class Append(DictModel):
        nums: list[int]

        @field_validator("nums")
        @classmethod
        def append(cls, value):
            return value + [0]

    m = Append(nums=[1])
    with pytest.raises(TypeError, match="topology"):
        m.nums.append(2)
    assert m.nums == [1, 0]
    state = {"fail": False}

    def factory():
        if state["fail"]:
            raise LookupError("factory failed")
        return 2

    class Defaults(DictModel):
        n: int = Field(default_factory=factory)

    d = Defaults(n=3)
    state["fail"] = True
    with pytest.raises(LookupError):
        d.reset("n")
    assert d.n == 3 and d.model_fields_set == {"n"}
    state["fail"] = False
    d.reset("n")
    assert d.n == 2 and d.model_fields_set == set()


def test_protocol_annotations_have_honest_runtime_types_and_adapter_inputs():
    from collections.abc import MutableMapping, MutableSequence, MutableSet
    from pydantic import TypeAdapter
    import json

    class Protocols(DictModel):
        sequence: MutableSequence[int]
        mapping: MutableMapping[str, int]
        bag: MutableSet[int]

    m = Protocols(sequence=[1], mapping={"a": 2}, bag={3})
    for value, annotation, abc, expected in [
        (m.sequence, list[int], MutableSequence, [1]),
        (m.mapping, dict[str, int], MutableMapping, {"a": 2}),
        (m.bag, set[int], MutableSet, {3}),
    ]:
        assert isinstance(value, abc)
        assert TypeAdapter(annotation).validate_python(value) == expected
        # Unsupported concrete JSON consumption must fail, never emit empty data.
        with pytest.raises(TypeError):
            json.dumps(value)
    m.sequence.append("2")
    m.mapping["b"] = "3"
    m.bag.add("4")
    assert m.model_dump() == {
        "sequence": [1, 2],
        "mapping": {"a": 2, "b": 3},
        "bag": {3, 4},
    }


@pytest.mark.parametrize("mode", ["python", "json", "strings"])
def test_explicit_public_alias_flags(mode):
    import json

    class Alias(DictModel):
        n: int = Field(default=1, alias="number")

    value = {"n": "2"}
    if mode == "python":
        m = Alias.model_validate(value, by_name=True, by_alias=False)
    elif mode == "json":
        m = Alias.model_validate_json(json.dumps(value), by_name=True, by_alias=False)
    else:
        m = Alias.model_validate_strings(value, by_name=True, by_alias=False)
    assert m.n == 2
    with pytest.raises(ValidationError):
        Alias.model_validate({"n": 2})
    assert Alias.model_validate({"n": 2}, by_name=True).n == 2
    assert Alias.model_validate({"number": 2}, by_alias=True, by_name=False).n == 2
    with pytest.raises(TypeError):
        Alias.model_validate({"number": 2, "extra": 1}, extra="allow")
