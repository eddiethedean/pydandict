"""Sol verification that readable benchmark claims match recorded measurements."""

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_sol008_readable_benchmark_summaries_match_recorded_runs():
    record = json.loads((ROOT / "docs/research/phase-0.2-results.json").read_text())
    findings = (ROOT / "docs/research/phase-0.2-findings.md").read_text()
    problems = []
    for line in findings.splitlines():
        cells = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(cells) != 5 or cells[1] not in ("baseline", "candidate"):
            continue
        workload, operation = cells[0].split("/")
        measurements = [
            run["measurement"]["workloads"][workload]["operations"][operation]
            for run in record["benchmark"]["runs"][cells[1]]
        ]
        for cell, metric, tolerance in zip(
            cells[2:],
            ("median_ms", "p95_ms", "median_peak_bytes"),
            (0.0005, 0.0005, 0.5),
            strict=True,
        ):
            expected = statistics.median(measurement[metric] for measurement in measurements)
            if abs(float(cell) - expected) > tolerance:
                problems.append(f"{cells[1]}/{cells[0]} {metric}: {cell} versus {expected}")
    assert not problems, "readable benchmark disagrees with recorded runs: " + "; ".join(problems)
