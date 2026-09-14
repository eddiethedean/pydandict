"""Reproducible feasibility measurements, not release performance budgets."""

from collections.abc import MutableSequence
from statistics import median
from time import perf_counter_ns
import gc
import tracemalloc
import weakref

from pydantic import Field
from pydandict_prototype import DictModel


class Record(DictModel):
    revision: int = 0
    numbers: MutableSequence[int] = Field(default_factory=list)


def run():
    rows = []
    for size in (10, 100, 1000):
        m = Record(numbers=list(range(size)))
        for index in range(5):
            m.revision = index
        samples = []
        for index in range(30):
            start = perf_counter_ns()
            m.revision = index
            samples.append((perf_counter_ns() - start) / 1000)
        start = perf_counter_ns()
        for _ in range(10000):
            m["revision"]
        read_ns = (perf_counter_ns() - start) / 10000
        tracemalloc.start()
        m.revision = 100
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        rows.append(
            {
                "elements": size,
                "scalar_write_median_us": round(median(samples), 2),
                "scalar_write_max_us": round(max(samples), 2),
                "key_read_mean_ns": round(read_ns, 2),
                "write_peak_traced_bytes": peak,
                "samples": 30,
                "warmup_writes": 5,
            }
        )
    m = Record(numbers=[1])
    replaced = []
    for _ in range(500):
        replaced.append(weakref.ref(m.numbers))
        m.numbers = [1]
    gc.collect()
    assert all(ref() is None for ref in replaced)
    assert len(m._pd_nodes) == 2
    return {
        "workloads": rows,
        "released_replaced_handles": len(replaced),
        "current_owned_nodes_after_500_replacements": len(m._pd_nodes),
        "scope": "Local feasibility observations; no cross-machine budget or throughput claim.",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run(), indent=2))
