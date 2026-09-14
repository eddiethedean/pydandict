from __future__ import annotations

import copy
import gc
import json
import pickle
import weakref
from collections.abc import Mapping, MutableMapping, MutableSequence, MutableSet
from typing import Any, Self

import pytest
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    computed_field,
    field_serializer,
    field_validator,
    model_serializer,
    model_validator,
)

from pydandict import DictModel


class Child(DictModel):
    cost: int = Field(ge=0)
    labels: MutableSequence[str] = Field(default_factory=list)


class Budget(DictModel):
    ceiling: int = Field(default=20, ge=0)
    costs: MutableSequence[int] = Field(default_factory=list)
    child: Child = Field(default_factory=lambda: Child(cost=1))
    table: MutableMapping[str, MutableSequence[int]] = Field(default_factory=dict)
    flags: MutableSet[int] = Field(default_factory=set)

    @model_validator(mode="after")
    def within_budget(self) -> Self:
        if (
            sum(self.costs) + self.child.cost + sum(sum(v) for v in self.table.values())
            > self.ceiling
        ):
            raise ValueError("budget exceeded")
        return self


class Bounds(DictModel):
    low: int = 1
    high: int = 3
    label: str = Field(default="home", alias="displayLabel")

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.low > self.high:
            raise ValueError("low exceeds high")
        return self


class Extras(DictModel):
    model_config = ConfigDict(extra="allow")
    x: int = 1


def snapshot(m):
    return m.model_dump_json(), m.model_fields_set, tuple(m)


def test_identity_serialization_and_mapping_views():
    m = Budget(costs=[2], table={"a": [3]}, flags={1})
    assert isinstance(m, BaseModel) and isinstance(m, Mapping) and isinstance(m, MutableMapping)
    assert m["costs"] is m.costs
    assert (
        isinstance(m.costs, MutableSequence)
        and isinstance(m.table, MutableMapping)
        and isinstance(m.flags, MutableSet)
    )
    assert dict(m)["costs"] is m.costs
    assert {**m}["child"] is m.child
    assert list(m) == ["ceiling", "costs", "child", "table", "flags"]
    assert json.loads(m.model_dump_json())["table"] == {"a": [3]}
    assert m.model_dump()["flags"] == {1}
    assert m.model_json_schema()["properties"]["costs"]["items"]["type"] == "integer"
    assert "_pd_" not in json.dumps(m.model_json_schema())
    view = m.values()
    m.ceiling = 21
    assert next(iter(view)) == 21


def test_coupled_updates_rollback_aliases_and_defaults():
    m = Bounds()
    assert m.model_fields_set == set()
    m.update(low=5, high=8)
    assert (m.low, m.high) == (5, 8)
    before = snapshot(m)
    with pytest.raises(ValidationError):
        m.low = 9
    assert snapshot(m) == before
    m.update([("low", 4), ("low", 6)], high=10)
    assert m.low == 6
    m.reset("low", "high", "low")
    assert (m.low, m.high) == (1, 3)
    assert m.model_fields_set == set()
    assert m.model_dump(exclude_unset=True) == {}
    aliased = Bounds.model_validate({"displayLabel": "x"})
    aliased["label"] = "y"
    assert aliased.model_dump(by_alias=True)["displayLabel"] == "y"
    assert "displayLabel" not in aliased


def test_late_generator_and_reentrancy_recover():
    m = Bounds()
    before = snapshot(m)

    def broken():
        yield ("low", 2)
        raise LookupError("late")

    with pytest.raises(LookupError):
        m.update(broken())
    assert snapshot(m) == before

    def reenter():
        m.low = 2
        yield ("high", 4)

    with pytest.raises(RuntimeError, match="reentrant"):
        m.update(reenter())
    assert snapshot(m) == before
    m.low = 2
    assert m.low == 2


@pytest.mark.parametrize("phase", ["staged", "validated", "result", "prepared"])
def test_fault_injection_preserves_state_handles_and_recovery(phase):
    m = Budget(costs=[1])
    handle, child = m.costs, m.child
    before = snapshot(m)

    def fail(where):
        if where == phase:
            raise RuntimeError("injected")

    Budget._prototype_fault = fail
    try:
        with pytest.raises(RuntimeError, match="injected"):
            handle.append(2)
    finally:
        Budget._prototype_fault = None
    assert snapshot(m) == before and m.costs is handle and m.child is child
    handle.append(2)
    assert m.costs == [1, 2]


def test_nested_parent_constraints_aliases_and_coercion():
    input_list = [2]
    original = Child(cost=3)
    m = Budget(ceiling=8, costs=input_list, child=original)
    input_list.append(100)
    original.cost = 100
    assert m.costs == [2] and m.child.cost == 3
    child, costs = m.child, dict(m)["costs"]
    before = snapshot(m)
    with pytest.raises(ValidationError):
        costs.append(9)
    with pytest.raises(ValidationError):
        child.cost = 9
    assert snapshot(m) == before and m.child is child and m.costs is costs
    child.cost = "4"
    assert child.cost == 4
    costs.append("1")
    assert costs == [2, 1]
    assert m.model_fields_set == {"ceiling", "costs", "child"}


def test_stale_handles_and_detached_removal_results():
    m = Extras(payload={"a": [1]})
    old = m["payload"]
    old_child = old["a"]
    removed = m.pop("payload")
    removed["a"].append(2)
    assert removed == {"a": [1, 2]}
    for operation in [
        lambda: len(old),
        lambda: list(old),
        lambda: old.get("a"),
        lambda: old_child.append(3),
        lambda: repr(old_child),
    ]:
        with pytest.raises(RuntimeError, match="stale"):
            operation()
    m = Budget(costs=[1])
    h = m.costs
    m.costs = [2]
    with pytest.raises(RuntimeError):
        h[0]
    assert m.costs == [2]


def test_node_identity_survives_reorder_and_unrelated_update():
    class Tree(DictModel):
        children: MutableSequence[Child]
        name: str = "x"

    m = Tree(children=[Child(cost=1), Child(cost=2)])
    a, b = m.children
    m.children.reverse()
    assert m.children[0] is b and m.children[1] is a
    a.cost = 4
    assert m.children[1].cost == 4
    m.name = "y"
    assert m.children[0] is b and m.children[1] is a
    removed = m.children.pop()
    assert removed.cost == 4
    removed.cost = 8
    with pytest.raises(RuntimeError):
        a.cost


def test_augmented_assignment_exactly_one_transaction():
    m = Budget(costs=[1], table={"a": [2]}, flags={1})
    calls = []
    Budget._prototype_fault = lambda phase: calls.append(phase)
    try:
        m.costs += [2]
        m["costs"] += [3]
        m.table["a"] += [1]
        m.flags |= {2}
    finally:
        Budget._prototype_fault = None
    assert calls.count("prepared") == 4
    assert m.costs == [1, 2, 3] and m.table["a"] == [2, 1] and m.flags == {1, 2}


def test_frozen_ancestors_and_copy():
    class Frozen(DictModel):
        model_config = ConfigDict(frozen=True)
        payload: MutableSequence[int]

    class Partial(DictModel):
        child: Child = Field(frozen=True)

    m = Frozen(payload=[1])
    for change in [lambda: m.payload.append(2), lambda: m.update(payload=[2])]:
        with pytest.raises(ValidationError):
            change()
    p = Partial(child=Child(cost=1))
    with pytest.raises(ValidationError):
        p.child.cost = 3
    with pytest.raises(ValidationError):
        p.child.labels.append("x")
    copied = m.model_copy(update={"payload": [2]})
    assert copied.payload == [2] and m.payload == [1]
    with pytest.raises(ValidationError):
        m.model_copy(update={"payload": ["bad"]})


@pytest.mark.parametrize("method", [copy.copy, copy.deepcopy, lambda m: m.model_copy()])
def test_copy_ownership(method):
    m = Budget(costs=[1])
    other = method(m)
    other.costs.append(2)
    other.child.cost = 3
    assert m.costs == [1] and m.child.cost == 1
    assert other.costs is not m.costs and other.child is not m.child


def test_extras_destructive_metadata_and_errors():
    m = Extras(a=2)
    view = m.items()
    it = iter(m)
    assert next(it) == "x"
    m["b"] = [3]
    with pytest.raises(RuntimeError):
        next(it)
    assert list(view)[-1][0] == "b"
    m.model_fields_set.clear()
    m.model_extra.clear()
    assert "a" in m and "a" in m.model_fields_set
    assert m.popitem() == ("b", [3])
    assert m.pop("a") == 2
    assert m.pop("missing", 7) == 7
    for operation in [
        lambda: m.pop("x", 0),
        lambda: m.clear(),
        lambda: m.reset("required"),
    ]:
        with pytest.raises((ValidationError, KeyError)):
            operation()
    assert m.setdefault("x", object()) == 1
    assert m.setdefault("new", [1]) is m["new"]
    with pytest.raises(TypeError):
        m[1] = 4
    with pytest.raises(TypeError):
        Extras(items=2)

    class Empty(DictModel):
        model_config = ConfigDict(extra="allow")

    e = Empty(a=1, b=2)
    e.clear()
    assert dict(e) == {} and e.model_fields_set == set()


def test_all_construction_paths_and_frameworks():
    source = {"costs": [2], "child": {"cost": 3}}
    for m in [
        Budget.model_validate(source),
        Budget.model_validate_json(json.dumps(source)),
        TypeAdapter(Budget).validate_python(source),
    ]:
        with pytest.raises(ValidationError):
            m.child.cost = 100
        assert m.model_dump()["costs"] == [2]
    assert Bounds.model_validate_strings({"low": "1", "high": "4"}).high == 4

    class Envelope(BaseModel):
        record: Budget

    envelope = Envelope.model_validate({"record": source})
    with pytest.raises(ValidationError):
        envelope.record.costs.append(100)
    app = FastAPI()

    @app.post("/budget", response_model=Budget)
    def endpoint(body: Budget) -> Budget:
        body.costs.append(1)
        return body

    with TestClient(app) as client:
        response = client.post("/budget", json=source)
        assert response.status_code == 200, response.text
        assert response.json()["costs"] == [2, 1]
        assert client.post("/budget", json={"ceiling": -1}).status_code == 422
        schema = client.get("/openapi.json").json()
        assert "_pd_" not in json.dumps(schema)
    assert jsonable_encoder(Budget(costs=[2]))["costs"] == [2]


def test_serializers_exclusions_computed_and_context():
    class Rich(DictModel):
        nums: MutableSequence[int]
        hidden: str = Field(default="secret", exclude=True)

        @field_serializer("nums")
        def encode(self, value: list[int], info):
            return [n * (info.context or {}).get("factor", 1) for n in value]

        @computed_field
        @property
        def total(self) -> int:
            return sum(self.nums)

    m = Rich(nums=[1, 2])
    assert m["hidden"] == "secret"
    assert m.model_dump(context={"factor": 2}) == {"nums": [2, 4], "total": 3}
    m.nums.append(3)
    assert m.model_dump() == {"nums": [1, 2, 3], "total": 6}
    assert m.nums == [1, 2, 3]

    class Encoded(DictModel):
        nums: MutableSequence[int]

        @model_serializer
        def encode(self) -> str:
            return ",".join(map(str, self.nums))

    encoded = Encoded(nums=[1, 2])
    assert encoded.model_dump() == "1,2"
    assert encoded["nums"] == [1, 2]


def test_nonidempotent_unchanged_normalizer_rejected_without_drift():
    class Doubler(DictModel):
        number: int
        label: str = "x"

        @field_validator("number")
        @classmethod
        def twice(cls, value: int) -> int:
            return value * 2

    m = Doubler(number=2)
    assert m.number == 4
    before = snapshot(m)
    with pytest.raises(TypeError, match="untouched"):
        m.label = "y"
    assert snapshot(m) == before
    # New input may be normalized once; this does not make the validator supported
    # for arbitrary later writes. The experiment deliberately exposes that limit.
    m.number = 3
    assert m.number == 6


def test_validator_topology_changes_fail_safely():
    class Reverse(DictModel):
        children: MutableSequence[Child]

        @field_validator("children")
        @classmethod
        def reverse(cls, value):
            return list(reversed(value))

    m = Reverse(children=[Child(cost=1), Child(cost=2)])
    before = snapshot(m)
    with pytest.raises(TypeError, match="untouched"):
        m.children.reverse()
    assert snapshot(m) == before


def test_unsafe_inputs_hooks_and_trusted_paths_rejected():
    class Broad(DictModel):
        payload: Any

    cycle = []
    cycle.append(cycle)

    class Plain(BaseModel):
        x: int = 1

    for value in [cycle, object(), Plain()]:
        with pytest.raises(TypeError):
            Broad(payload=value)
    with pytest.raises(TypeError):
        Bounds.model_construct(low=100)
    with pytest.raises(TypeError):
        pickle.dumps(Bounds())
    with pytest.raises(TypeError):

        class Hook(DictModel):
            def model_post_init(self, context):
                pass

    with pytest.raises(TypeError):

        class Disabled(DictModel):
            model_config = ConfigDict(validate_assignment=False)


def test_root_lifetime_and_collection():
    m = Budget(costs=[1])
    ref = weakref.ref(m)
    h = m.costs
    del m
    gc.collect()
    assert ref() is not None
    h.append(2)
    assert h == [1, 2]
    del h
    gc.collect()
    assert ref() is None


@given(st.lists(st.integers(min_value=-10, max_value=30), min_size=1, max_size=50))
@settings(max_examples=100, deadline=None)
def test_generated_nested_transactions(values):
    m = Budget(ceiling=20, child=Child(cost=0))
    expected = []
    handle = m.costs
    for value in values:
        before = snapshot(m)
        if sum(expected) + value <= 20:
            handle.append(value)
            expected.append(value)
        else:
            with pytest.raises(ValidationError):
                handle.append(value)
            assert snapshot(m) == before
        assert m.costs == expected and m.costs is handle
        assert m.model_dump()["costs"] == expected


@pytest.mark.parametrize("fail_at", [1, 2, 5, 10])
@pytest.mark.parametrize("after_swap", [False, True])
def test_commit_slot_failure_restores_all_live_state(monkeypatch, fail_at, after_swap):
    from pydandict import _core

    m = Budget(costs=[1], table={"a": [1]})
    costs, child, table = m.costs, m.child, m.table
    before = snapshot(m)
    original = _core._swap
    calls = 0

    def failing(target, name, value):
        nonlocal calls
        calls += 1
        if calls == fail_at and not after_swap:
            raise MemoryError("injected slot failure")
        original(target, name, value)
        if calls == fail_at and after_swap:
            raise MemoryError("injected slot failure")

    with monkeypatch.context() as patch:
        patch.setattr(_core, "_swap", failing)
        with pytest.raises(MemoryError):
            m.costs.append(2)
    assert snapshot(m) == before
    assert m.costs is costs and m.child is child and m.table is table
    m.costs.append(2)
    assert costs == [1, 2]


def test_properties_do_not_shadow_extra_mapping_state():
    class ReadOnly(Extras):
        @property
        def total(self):
            return self.x * 2

    with pytest.raises(TypeError, match="protected"):
        ReadOnly(total=1)
    with pytest.raises(TypeError, match="writable"):

        class Writable(DictModel):
            x: int

            @property
            def alias(self):
                return self.x

            @alias.setter
            def alias(self, value):
                self.x = value
