"""Produce a reproducible, observational Phase 0.2 benchmark report."""

from __future__ import annotations

import json
import platform
import statistics
import time
import tracemalloc
from collections.abc import Callable, MutableSequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import pydantic

from pydandict import DictModel


@dataclass(frozen=True)
class Sample:
    milliseconds: float
    peak_bytes: int


class Record(DictModel):
    numbers: MutableSequence[int]


def measure(operation: Callable[[], None], repeats: int) -> list[Sample]:
    samples: list[Sample] = []
    for _ in range(repeats):
        tracemalloc.start()
        started = time.perf_counter()
        operation()
        elapsed = (time.perf_counter() - started) * 1000
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        samples.append(Sample(elapsed, peak))
    return samples


def summarize(samples: list[Sample]) -> dict[str, float]:
    return {
        "median_ms": statistics.median(sample.milliseconds for sample in samples),
        "median_peak_bytes": statistics.median(sample.peak_bytes for sample in samples),
    }


def main() -> int:
    repeats = 3
    width = 1000

    def baseline() -> None:
        data = {"numbers": list(range(width))}
        data["numbers"][0] = -1

    def candidate() -> None:
        model = Record(numbers=list(range(width)))
        model.numbers[0] = -1

    baseline_samples = measure(baseline, repeats)
    candidate_samples = measure(candidate, repeats)
    report: dict[str, Any] = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "pydantic": pydantic.__version__,
        "pydandict": "0.1.0",
        "repeats": repeats,
        "workloads": {"large_values": {"width": width}},
        "baseline": summarize(baseline_samples),
        "candidate": summarize(candidate_samples),
    }
    if len(Record(numbers=[1]).numbers) != 1:
        raise RuntimeError("benchmark workload did not produce a validated list")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
