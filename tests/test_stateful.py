"""Mixed operation sequences against an independent plain-data oracle."""

from collections.abc import MutableMapping, MutableSequence, MutableSet

import pytest
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule
from pydantic import ConfigDict, Field, ValidationError, model_validator

from pydandict import DictModel


class State(DictModel):
    limit: int = Field(default=20, ge=0)
    costs: MutableSequence[int] = Field(default_factory=list)
    charges: MutableMapping[str, int] = Field(default_factory=dict)
    flags: MutableSet[int] = Field(default_factory=set)

    @model_validator(mode="after")
    def bounded(self):
        if sum(self.costs) + sum(self.charges.values()) > self.limit:
            raise ValueError("total exceeds limit")
        return self


class Transactions(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.model = State()
        self.costs = []
        self.charges = {}
        self.flags = set()
        self.limit = 20
        self.stale = []

    @rule(value=st.integers(-5, 30))
    def append(self, value):
        before = self.model.model_dump_json(), self.model.model_fields_set
        if sum(self.costs) + sum(self.charges.values()) + value > self.limit:
            try:
                self.model.costs.append(value)
            except ValidationError:
                pass
            else:
                raise AssertionError("invalid append accepted")
            assert (self.model.model_dump_json(), self.model.model_fields_set) == before
        else:
            self.model.costs.append(value)
            self.costs.append(value)

    @rule(key=st.sampled_from(["a", "b", "c"]), value=st.integers(-5, 30))
    def assign_charge(self, key, value):
        new = dict(self.charges, **{key: value})
        if sum(self.costs) + sum(new.values()) > self.limit:
            try:
                self.model.charges[key] = value
            except ValidationError:
                pass
            else:
                raise AssertionError("invalid mapping write accepted")
        else:
            self.model.charges[key] = value
            self.charges = new

    @rule(value=st.integers(0, 40))
    def change_limit(self, value):
        if sum(self.costs) + sum(self.charges.values()) > value:
            try:
                self.model.limit = value
            except ValidationError:
                pass
            else:
                raise AssertionError("invalid root write accepted")
        else:
            self.model.limit = value
            self.limit = value

    @rule(value=st.integers(0, 10))
    def flag(self, value):
        self.model.flags ^= {value}
        self.flags ^= {value}

    @rule()
    def reverse(self):
        self.model.costs.reverse()
        self.costs.reverse()

    @rule()
    def replace_and_keep_stale(self):
        old = self.model.costs
        self.model.costs = list(self.costs)
        self.stale.append(old)
        for handle in self.stale[-3:]:
            try:
                handle.append(1)
            except RuntimeError:
                pass
            else:
                raise AssertionError("stale handle accepted a write")

    @rule()
    def copy_isolation(self):
        other = self.model.model_copy()
        other.update(limit=100, costs=[1], charges={})
        other.costs.append(2)
        assert other.costs == [1, 2]
        assert self.model.costs == self.costs

    @rule()
    def coupled_reset(self):
        self.model.update(limit=20, costs=[], charges={})
        self.costs, self.charges, self.limit = [], {}, 20

    @invariant()
    def oracle_agrees(self):
        expected = {
            "limit": self.limit,
            "costs": self.costs,
            "charges": self.charges,
            "flags": self.flags,
        }
        assert self.model.model_dump() == expected
        assert self.model.costs == self.costs
        assert sum(self.costs) + sum(self.charges.values()) <= self.limit


TestTransactions = Transactions.TestCase
TestTransactions.settings = settings(
    max_examples=100, stateful_step_count=100, deadline=None, derandomize=True
)


class ScalarState(DictModel):
    model_config = ConfigDict(extra="allow")

    low: int = Field(default=1, ge=0)
    high: int = Field(default=3, ge=0)

    @model_validator(mode="after")
    def ordered(self):
        if self.low > self.high:
            raise ValueError("low must not exceed high")
        return self


class ScalarTransactions(RuleBasedStateMachine):
    """Independent scalar values/order/fields-set oracle for Phase 0.3."""

    def __init__(self):
        super().__init__()
        self.model = ScalarState()
        self.values = {"low": 1, "high": 3}
        self.order = ["low", "high"]
        self.fields_set = set()

    def snapshot(self):
        return dict(self.model), tuple(self.model), set(self.model.model_fields_set)

    def assert_oracle(self):
        assert dict(self.model) == self.values
        assert tuple(self.model) == tuple(self.order)
        assert self.model.model_fields_set == self.fields_set

    @rule(value=st.integers(min_value=0, max_value=12))
    def set_low(self, value):
        before = self.snapshot()
        if value > self.values["high"]:
            with pytest.raises(ValidationError):
                self.model.low = value
        else:
            self.model.low = value
            self.values["low"] = value
            self.fields_set.add("low")
        assert self.snapshot() == before if value > self.values["high"] else True
        self.assert_oracle()

    @rule(value=st.integers(min_value=0, max_value=12))
    def set_high(self, value):
        before = self.snapshot()
        if value < self.values["low"]:
            with pytest.raises(ValidationError):
                self.model.high = value
        else:
            self.model.high = value
            self.values["high"] = value
            self.fields_set.add("high")
        assert self.snapshot() == before if value < self.values["low"] else True
        self.assert_oracle()

    @rule(low=st.integers(0, 12), high=st.integers(0, 12))
    def coupled_update(self, low, high):
        before = self.snapshot()
        if low > high:
            with pytest.raises(ValidationError):
                self.model.update(low=low, high=high)
        else:
            self.model.update(low=low, high=high)
            self.values.update(low=low, high=high)
            self.fields_set.update(("low", "high"))
        if low > high:
            assert self.snapshot() == before
        self.assert_oracle()

    @rule(key=st.sampled_from(["a", "b", "c"]), value=st.integers(-5, 20))
    def extra_write(self, key, value):
        existed = key in self.values
        self.model[key] = value
        self.values[key] = value
        if not existed:
            self.order.append(key)
        self.fields_set.add(key)
        self.assert_oracle()

    @rule(key=st.sampled_from(["a", "b", "c"]))
    def extra_pop(self, key):
        before = self.snapshot()
        existed = key in self.values
        if not existed:
            with pytest.raises(KeyError):
                self.model.pop(key)
        else:
            assert self.model.pop(key) == self.values.pop(key)
            self.order.remove(key)
            self.fields_set.discard(key)
        if not existed:
            assert self.snapshot() == before
        self.assert_oracle()

    @rule()
    def reset_defaults(self):
        self.model.reset("low", "high")
        self.values.update(low=1, high=3)
        self.fields_set.difference_update(("low", "high"))
        self.assert_oracle()

    @rule()
    def no_op(self):
        before = self.snapshot()
        self.model.update()
        self.model.setdefault("low", object())
        assert self.snapshot() == before
        self.assert_oracle()


TestScalarTransactions = ScalarTransactions.TestCase
TestScalarTransactions.settings = settings(
    max_examples=100, stateful_step_count=100, deadline=None, derandomize=True
)
