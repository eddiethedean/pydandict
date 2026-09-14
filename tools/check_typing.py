"""Run the repository's positive and negative strict typing checks."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[1]


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def _report(result: subprocess.CompletedProcess[str], label: str) -> dict[str, Any]:
    if not result.stdout.strip():
        raise SystemExit(f"{label} produced no JSON output:\n{result.stderr}")
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"{label} produced invalid JSON:\n{result.stdout}\n{result.stderr}"
        ) from exc
    summary = report.get("summary", {})
    if not isinstance(summary, dict):
        raise SystemExit(f"{label} did not return a Pyright summary")
    return report


def _check_positive() -> None:
    result = _run([sys.executable, "-m", "pyright", "--project", "pyproject.toml", "--outputjson"])
    report = _report(result, "positive typing check")
    summary = report["summary"]
    if result.returncode != 0 or summary.get("errorCount") != 0:
        raise SystemExit(f"positive typing check failed:\n{result.stdout}\n{result.stderr}")
    if summary.get("filesAnalyzed", 0) < 2:
        raise SystemExit("positive typing check analyzed fewer than two intended files")


def _expected_diagnostics(path: Path) -> set[tuple[int, str]]:
    expected: set[tuple[int, str]] = set()
    pattern = re.compile(r"#\s*expected:\s*([A-Za-z0-9_]+)")
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        match = pattern.search(line)
        if match:
            expected.add((line_number, match.group(1)))
    return expected


def _check_negative() -> None:
    source = ROOT / "tests" / "typing_negative.py"
    expected = _expected_diagnostics(source)
    with tempfile.TemporaryDirectory(prefix="pydandict-typing-") as temporary:
        directory = Path(temporary)
        fixture = directory / source.name
        shutil.copy2(source, fixture)
        config = {
            "include": [fixture.name],
            "exclude": [],
            "extraPaths": [str(ROOT / "src")],
            "pythonVersion": "3.11",
            "typeCheckingMode": "strict",
        }
        project = directory / "pyrightconfig.json"
        project.write_text(json.dumps(config))
        result = _run([sys.executable, "-m", "pyright", "--project", str(project), "--outputjson"])
        report = _report(result, "negative typing check")
        diagnostics = report.get("generalDiagnostics", [])
        actual: set[tuple[int, str]] = set()
        for raw_diagnostic in diagnostics:
            if not isinstance(raw_diagnostic, dict):
                continue
            diagnostic = cast(dict[str, Any], raw_diagnostic)
            range_data: Any = diagnostic.get("range", {})
            location: dict[str, Any] = {}
            if isinstance(range_data, dict):
                start_data: Any = cast(dict[str, Any], range_data).get("start", {})
                if isinstance(start_data, dict):
                    location = cast(dict[str, Any], start_data)
            line: Any = location.get("line")
            rule: Any = diagnostic.get("rule")
            if isinstance(line, int) and isinstance(rule, str):
                actual.add((line + 1, rule))
        if result.returncode == 0 or actual != expected:
            raise SystemExit(
                "negative typing check did not match its expected diagnostics:\n"
                f"expected={sorted(expected)!r}\nactual={sorted(actual)!r}\n"
                f"{result.stdout}\n{result.stderr}"
            )
        if report.get("summary", {}).get("filesAnalyzed") != 1:
            raise SystemExit("negative typing check did not analyze exactly one fixture")


def main() -> int:
    _check_positive()
    _check_negative()
    print("strict positive and negative typing checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
