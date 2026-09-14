"""Mixed operation sequences against an independent plain-data oracle."""

from collections.abc import MutableMapping, MutableSequence, MutableSet

from hypothesis import settings, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule
from pydantic import Field, ValidationError, model_validator

from pydandict_prototype import DictModel


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
