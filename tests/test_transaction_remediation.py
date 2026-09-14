"""Recovery and retention checks for the adapter/coordinator remediation."""

import gc
import weakref
from collections.abc import MutableSequence

import pytest
from test_prototype import Budget, snapshot

from pydandict import DictModel, _core


def test_every_prepared_swap_boundary_recovers(monkeypatch):
    original = _core._swap
    count = 0

    def counting(target, name, value):
        nonlocal count
        count += 1
        original(target, name, value)

    probe = Budget(costs=[1], table={"a": [1]})
    with monkeypatch.context() as patch:
        patch.setattr(_core, "_swap", counting)
        probe.update(ceiling=30, costs=[1, 2])
    assert count > 0

    for boundary in range(1, count + 1):
        for after in (False, True):
            model = Budget(costs=[1], table={"a": [1]})
            handles = model.costs, model.child, model.table, model.table["a"]
            before = snapshot(model)
            swaps = 0

            def failing(target, name, value):
                nonlocal swaps
                swaps += 1
                if swaps == boundary and not after:
                    raise KeyboardInterrupt("before swap")
                original(target, name, value)
                if swaps == boundary and after:
                    raise KeyboardInterrupt("after swap")

            with monkeypatch.context() as patch:
                patch.setattr(_core, "_swap", failing)
                with pytest.raises(KeyboardInterrupt):
                    model.update(ceiling=30, costs=[1, 2])
            assert snapshot(model) == before
            assert all(
                previous is current
                for previous, current in zip(
                    handles, (model.costs, model.child, model.table, model.table["a"])
                )
            )
            assert not model._pd_busy
            assert not _core._BUILDING.get() and not _core._CANONICAL.get()
            model.costs.append(2)
            assert model.costs == [1, 2]


def test_replacements_collect_discarded_handles_and_bound_bookkeeping():
    class Record(DictModel):
        numbers: MutableSequence[int]

    model = Record(numbers=[0])
    discarded = []
    for value in range(500):
        discarded.append(weakref.ref(model.numbers))
        model.numbers = [value]
    gc.collect()
    assert all(reference() is None for reference in discarded)
    assert len(model._pd_nodes) == 2
    assert model.numbers == [499]
