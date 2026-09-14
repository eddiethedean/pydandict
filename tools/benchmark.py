"""Measure the approved production baseline and candidate in isolated processes."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc
from collections.abc import Callable, MutableMapping, MutableSequence, MutableSet
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar, Self, cast

from pydantic import Field, ValidationError, model_validator

from pydandict import DictModel

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "07fec9b7eafef5b00befe9fa24ccd012ce0232a1"
WARMUPS = 5
SAMPLES = 100
READS = 10000
ALLOCATION_SAMPLES = 10
RUNS = 3
_root_calls = 0
JsonObject = dict[str, object]


class Flat(DictModel):
    left: int = 0
    numbers: MutableSequence[int]

    @model_validator(mode="after")
    def count_root(self) -> Self:
        global _root_calls
        _root_calls += 1
        return self


def _empty_children() -> list[Chain]:
    return []


class Chain(DictModel):
    left: int
    right: int
    children: MutableSequence[Chain] = Field(default_factory=_empty_children)

    @model_validator(mode="after")
    def count_root(self) -> Self:
        global _root_calls
        # The second scalar is a stable root marker; intermediate nodes are not
        # root validation invocations, even though they share this model class.
        if self.right == -1:
            _root_calls += 1
        return self


class RootChain(Chain):
    """Distinct root schema; recursive children use Chain and two scalar leaves."""


class Mixed(DictModel):
    limit: int = 10
    numbers: MutableSequence[int]
    table: MutableMapping[str, int]
    flags: MutableSet[int]
    f0: int = 0
    f1: int = 0
    f2: int = 0
    f3: int = 0
    f4: int = 0
    f5: int = 0
    f6: int = 0
    f7: int = 0
    f8: int = 0
    f9: int = 0
    batch_fields: ClassVar[tuple[str, ...]] = tuple(f"f{i}" for i in range(10))

    @model_validator(mode="after")
    def parent_constraint(self) -> Self:
        global _root_calls
        _root_calls += 1
        if sum(self.numbers) + sum(self.table.values()) + sum(self.flags) > self.limit:
            raise ValueError("parent sum exceeds limit")
        if len({self[name] for name in self.batch_fields}) != 1:
            raise ValueError("ten coupled fields must agree")
        return self


@dataclass
class Workload:
    name: str
    model: DictModel
    expected: JsonObject
    scalar: str
    leaf: Callable[[int], None]
    expected_leaf: Callable[[int], None]
    shape: JsonObject


def _chain_input(depth: int, *, root: bool = True) -> JsonObject:
    return {
        "left": 0,
        "right": -1 if root else 0,
        "children": [_chain_input(depth - 1, root=False)] if depth > 1 else [],
    }


def _counts(value: object) -> JsonObject:
    totals = {"models": 0, "sequences": 0, "mappings": 0, "sets": 0, "scalar_leaves": 0}

    def visit(node: object, *, model: bool = False) -> None:
        if isinstance(node, dict):
            totals["models" if model else "mappings"] += 1
            for key, child in cast(dict[str, object], node).items():
                if key == "children":
                    totals["sequences"] += 1
                    for child_model in cast(list[JsonObject], child):
                        visit(child_model, model=True)
                else:
                    visit(child)
        elif isinstance(node, list):
            totals["sequences"] += 1
            for child in cast(list[object], node):
                visit(child)
        elif isinstance(node, set):
            totals["sets"] += 1
            totals["scalar_leaves"] += len(cast(set[object], node))
        else:
            totals["scalar_leaves"] += 1

    visit(value, model=True)
    return {
        **totals,
        "owned_nodes": sum(totals[key] for key in ("models", "sequences", "mappings", "sets")),
    }


def workloads() -> list[Workload]:
    result: list[Workload] = []
    for width in (10, 100, 1000, 10000):
        expected: JsonObject = {"left": 0, "numbers": list(range(width))}
        model = Flat.model_validate(expected)

        def set_leaf(value: int, current: Flat = model) -> None:
            current.numbers[0] = value

        def expected_leaf(value: int, current: JsonObject = expected) -> None:
            cast(list[int], current["numbers"])[0] = value

        result.append(
            Workload(
                f"flat_{width}",
                model,
                expected,
                "left",
                set_leaf,
                expected_leaf,
                {"kind": "flat", "width": width, **_counts(expected)},
            )
        )
    for depth in (1, 5, 20):
        chain_expected = _chain_input(depth)
        chain = RootChain.model_validate(chain_expected)
        leaf = chain
        leaf_expected = chain_expected
        for _ in range(depth - 1):
            leaf = leaf.children[0]
            leaf_expected = cast(list[JsonObject], leaf_expected["children"])[0]

        def chain_leaf(value: int, current: Chain = leaf) -> None:
            current.left = value

        def chain_expected_leaf(value: int, current: JsonObject = leaf_expected) -> None:
            current["left"] = value

        result.append(
            Workload(
                f"linear_{depth}",
                chain,
                chain_expected,
                "left",
                chain_leaf,
                chain_expected_leaf,
                {
                    "kind": "linear",
                    "depth": depth,
                    "branching": 1,
                    "scalar_leaves_per_level": 2,
                    **_counts(chain_expected),
                },
            )
        )
    mixed_expected: JsonObject = {
        "limit": 10,
        "numbers": [1, 2],
        "table": {"a": 3},
        "flags": {4},
        **{name: 0 for name in Mixed.batch_fields},
    }
    mixed = Mixed.model_validate(mixed_expected)

    def mixed_leaf(value: int) -> None:
        mixed.numbers[0] = value

    def mixed_expected_leaf(value: int) -> None:
        cast(list[int], mixed_expected["numbers"])[0] = value

    result.append(
        Workload(
            "mixed_parent",
            mixed,
            mixed_expected,
            "limit",
            mixed_leaf,
            mixed_expected_leaf,
            {
                "kind": "mixed",
                "parent_constraint": "sum(sequence)+sum(mapping.values)+sum(set)<=limit",
                "coupled_fields": 10,
                **_counts(mixed_expected),
            },
        )
    )
    return result


def _json_state(value: object) -> object:
    if isinstance(value, dict):
        return {key: _json_state(child) for key, child in cast(dict[str, object], value).items()}
    if isinstance(value, list):
        return [_json_state(child) for child in cast(list[object], value)]
    if isinstance(value, set):
        return sorted(cast(set[int], value))
    return value


@dataclass
class Operation:
    invoke: Callable[[], object]
    verify: Callable[[object], None]
    root_validations: int


def operations(workload: Workload) -> dict[str, Operation]:
    model, expected = workload.model, workload.expected

    def verify_state(_result: object) -> None:
        assert model.model_dump() == expected

    def read() -> object:
        return model[workload.scalar]

    def verify_read(value: object) -> None:
        assert value == expected[workload.scalar]

    scalar_value = 0

    def scalar() -> None:
        nonlocal scalar_value
        scalar_value = 1 - scalar_value
        value = scalar_value + (10 if isinstance(model, Mixed) else 0)
        model[workload.scalar] = value

    def verify_scalar(result: object) -> None:
        expected[workload.scalar] = scalar_value + (10 if isinstance(model, Mixed) else 0)
        verify_state(result)

    leaf_value = 0

    def leaf() -> None:
        nonlocal leaf_value
        leaf_value = 1 - leaf_value
        workload.leaf(leaf_value)

    def verify_leaf(result: object) -> None:
        workload.expected_leaf(leaf_value)
        verify_state(result)

    def copy() -> object:
        return model.model_copy()

    def verify_copy(value: object) -> None:
        assert isinstance(value, DictModel) and value is not model
        assert value.model_dump() == expected

    def python_dump() -> object:
        return model.model_dump()

    def verify_dump(value: object) -> None:
        assert value == expected

    def json_dump() -> object:
        return model.model_dump_json()

    def verify_json(value: object) -> None:
        assert isinstance(value, str) and json.loads(value) == _json_state(expected)

    result = {
        "key_read": Operation(read, verify_read, 0),
        "scalar_write": Operation(scalar, verify_scalar, 1),
        "nested_leaf": Operation(leaf, verify_leaf, 1),
        "copy": Operation(copy, verify_copy, 1),
        "python_dump": Operation(python_dump, verify_dump, 0),
        "json_dump": Operation(json_dump, verify_json, 0),
    }
    if isinstance(model, Mixed):
        batch_value = 0

        def batch() -> None:
            nonlocal batch_value
            batch_value = 1 - batch_value
            model.update({name: batch_value for name in Mixed.batch_fields})

        def verify_batch(value: object) -> None:
            expected.update({name: batch_value for name in Mixed.batch_fields})
            verify_state(value)

        def reject() -> None:
            try:
                model.numbers.append(100)
            except ValidationError:
                return
            raise AssertionError("parent-invalid edit committed")

        result["coupled_10field"] = Operation(batch, verify_batch, 1)
        result["rejected_parent"] = Operation(reject, verify_state, 1)
    return result


def _percentile(values: list[float], percentile: int) -> float:
    ordered = sorted(values)
    return ordered[max(0, (len(values) * percentile + 99) // 100 - 1)]


def measure(operation: Operation, samples: int) -> JsonObject:
    global _root_calls
    phases: dict[str, int] = {}

    def execute() -> object:
        before = _root_calls
        result = operation.invoke()
        operation.verify(result)
        assert _root_calls - before == operation.root_validations
        return result

    before = _root_calls
    for _ in range(WARMUPS):
        execute()
    phases["warmups"] = _root_calls - before
    before = _root_calls
    latency: list[float] = []
    for _ in range(samples):
        calls_before = _root_calls
        started = time.perf_counter_ns()
        result = operation.invoke()
        elapsed = time.perf_counter_ns() - started
        # Verification and tracemalloc are both outside latency measurement.
        operation.verify(result)
        assert _root_calls - calls_before == operation.root_validations
        latency.append(elapsed / 1_000_000)
    phases["timed"] = _root_calls - before
    before = _root_calls
    peaks: list[float] = []
    for _ in range(ALLOCATION_SAMPLES):
        tracemalloc.start()
        try:
            result = operation.invoke()
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        operation.verify(result)
        peaks.append(float(peak))
    phases["allocation"] = _root_calls - before
    assert phases["allocation"] == ALLOCATION_SAMPLES * operation.root_validations
    return {
        "samples": samples,
        "warmups": WARMUPS,
        "allocation_samples": ALLOCATION_SAMPLES,
        "median_ms": statistics.median(latency),
        "p95_ms": _percentile(latency, 95),
        "median_peak_bytes": statistics.median(peaks),
        "p95_peak_bytes": _percentile(peaks, 95),
        "max_peak_bytes": max(peaks),
        "root_validation_invocations": phases,
        "expected_root_validations_per_operation": operation.root_validations,
        "correctness": "asserted for every warmup, timed and allocation operation",
    }


def worker() -> JsonObject:
    import pydantic

    import pydandict

    results: JsonObject = {}
    for workload in workloads():
        assert workload.model.model_dump() == workload.expected
        metrics = {
            name: measure(operation, READS if name == "key_read" else SAMPLES)
            for name, operation in operations(workload).items()
        }
        results[workload.name] = {
            "shape": workload.shape,
            "operations": metrics,
            "not_applicable": []
            if isinstance(workload.model, Mixed)
            else [
                "coupled_10field: no ten-field constraint in this shape; measured on mixed_parent",
                "rejected_parent: no parent sum constraint in this shape; measured on mixed_parent",
            ],
        }
    return {
        "python": sys.version,
        "pydantic": pydantic.__version__,
        "import_root": str(Path(pydandict.__file__).resolve()),
        "workloads": results,
    }


def _command(args: list[str]) -> str:
    return subprocess.run(args, cwd=ROOT, check=True, text=True, capture_output=True).stdout.strip()


def _source_hashes(directory: Path) -> dict[str, str]:
    return {
        path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file() and (path.suffix == ".py" or path.name == "py.typed")
    }


def _baseline_source(directory: Path) -> None:
    files = _command(
        ["git", "ls-tree", "-r", "--name-only", BASELINE, "src/pydandict"]
    ).splitlines()
    if not files:
        raise RuntimeError("approved baseline is unavailable; fetch repository history")
    for filename in files:
        path = directory / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        content = subprocess.run(
            ["git", "show", f"{BASELINE}:{filename}"], cwd=ROOT, check=True, capture_output=True
        ).stdout
        path.write_bytes(content)


def _variability(runs: list[JsonObject]) -> JsonObject:
    grouped: dict[str, list[float]] = {}
    for run in runs:
        data = cast(JsonObject, cast(JsonObject, run["measurement"])["workloads"])
        for shape, raw in data.items():
            measurements = cast(JsonObject, cast(JsonObject, raw)["operations"])
            for name, metric in measurements.items():
                grouped.setdefault(f"{shape}/{name}", []).append(
                    float(cast(float, cast(JsonObject, metric)["median_ms"]))
                )
    return {
        name: {
            "run_medians_ms": values,
            "median_ms": statistics.median(values),
            "min_ms": min(values),
            "max_ms": max(values),
            "spread_percent_of_median": (max(values) - min(values))
            * 100
            / statistics.median(values),
        }
        for name, values in grouped.items()
    }


def main() -> int:
    head = _command(["git", "rev-parse", "HEAD"])
    dirty = _command(["git", "status", "--porcelain"])
    dependencies = dict(
        sorted(
            (distribution.metadata["Name"], distribution.version)
            for distribution in importlib.metadata.distributions()
            if distribution.metadata["Name"]
        )
    )
    all_runs: dict[str, list[JsonObject]] = {"baseline": [], "candidate": []}
    commands: list[JsonObject] = []
    with tempfile.TemporaryDirectory(prefix="pydandict-benchmark-") as temporary:
        directory = Path(temporary)
        baseline = directory / "baseline"
        candidate = directory / "candidate"
        _baseline_source(baseline)
        shutil.copytree(
            ROOT / "src",
            candidate / "src",
            ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"),
        )
        script = directory / "benchmark.py"
        shutil.copy2(Path(__file__), script)
        sources = {
            "baseline": {
                "commit": BASELINE,
                "dirty": False,
                "hashes": _source_hashes(baseline / "src"),
            },
            "candidate": {
                "commit": head,
                "dirty": bool(dirty),
                "git_status": dirty.splitlines(),
                "hashes": _source_hashes(candidate / "src"),
            },
        }
        for index in range(RUNS):
            order = ("baseline", "candidate") if index % 2 == 0 else ("candidate", "baseline")
            for label in order:
                print(
                    f"Measuring {label}, complete run {index + 1}/{RUNS}",
                    file=sys.stderr,
                    flush=True,
                )
                source = (directory / label / "src").resolve()
                environment = os.environ.copy()
                environment["PYTHONPATH"] = str(source)
                environment["PYTHONHASHSEED"] = "0"
                args = [sys.executable, str(script), "--worker"]
                commands.append(
                    {
                        "revision": label,
                        "run": index + 1,
                        "argv": args,
                        "cwd": str(directory),
                        "PYTHONPATH": str(source),
                        "PYTHONHASHSEED": "0",
                    }
                )
                completed = subprocess.run(
                    args, cwd=directory, env=environment, text=True, capture_output=True, check=True
                )
                measurement = cast(JsonObject, json.loads(completed.stdout))
                imported = Path(cast(str, measurement["import_root"]))
                assert imported.is_relative_to(source), (
                    f"benchmark imported the wrong production source: {imported}, expected {source}"
                )
                all_runs[label].append({"run": index + 1, "measurement": measurement})
        assert sources["candidate"]["hashes"] == _source_hashes(ROOT / "src"), (
            "source changed while measuring"
        )
        report: JsonObject = {
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "machine": {
                "platform": platform.platform(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "uname": platform.uname()._asdict(),
                "logical_cpus": os.cpu_count(),
                "python": sys.version,
                "executable": sys.executable,
            },
            "resolved_dependencies": dependencies,
            "sources": sources,
            "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "protocol": {
                "complete_runs_per_revision": RUNS,
                "warmups_per_operation": WARMUPS,
                "timed_samples_per_mutation_copy_dump": SAMPLES,
                "reads_per_shape_per_run": READS,
                "separate_allocation_samples_per_operation": ALLOCATION_SAMPLES,
                "latency_tracing_enabled": False,
                "timing_ceiling": None,
                "invocation": f"{sys.executable} tools/benchmark.py",
            },
            "commands": commands,
            "runs": all_runs,
            "variability": {label: _variability(runs) for label, runs in all_runs.items()},
        }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--worker"]:
        print(json.dumps(worker(), sort_keys=True))
    else:
        raise SystemExit(main())
