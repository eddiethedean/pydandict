"""Run the repository's positive and negative strict typing checks."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
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
    configuration = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["pyright"]
    intended = {
        "src",
        "tests/typing_positive.py",
        "tools/check_typing.py",
        "tools/qualify_package.py",
        "tools/benchmark.py",
    }
    if (
        set(configuration.get("include", [])) != intended
        or configuration.get("exclude") != ["tests/typing_negative.py"]
        or configuration.get("typeCheckingMode") != "strict"
    ):
        raise SystemExit("positive typing configuration does not cover the intended strict sources")
    result = _run([sys.executable, "-m", "pyright", "--project", "pyproject.toml", "--outputjson"])
    report = _report(result, "positive typing check")
    summary = report["summary"]
    if result.returncode != 0 or summary.get("errorCount") != 0:
        raise SystemExit(f"positive typing check failed:\n{result.stdout}\n{result.stderr}")
    expected_files = len(list((ROOT / "src").rglob("*.py"))) + 4
    if summary.get("filesAnalyzed") != expected_files:
        raise SystemExit(
            "positive typing check did not analyze every production, fixture and helper file: "
            f"expected={expected_files}, actual={summary.get('filesAnalyzed')!r}"
        )


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
        actual: list[tuple[int, str | None, str]] = []
        filenames: list[object] = []
        for raw_diagnostic in diagnostics:
            if not isinstance(raw_diagnostic, dict):
                raise SystemExit("negative typing check returned a malformed diagnostic")
            diagnostic = cast(dict[str, Any], raw_diagnostic)
            range_data: Any = diagnostic.get("range", {})
            location: dict[str, Any] = {}
            if isinstance(range_data, dict):
                start_data: Any = cast(dict[str, Any], range_data).get("start", {})
                if isinstance(start_data, dict):
                    location = cast(dict[str, Any], start_data)
            line: Any = location.get("line")
            rule: Any = diagnostic.get("rule")
            if not isinstance(line, int) or not isinstance(rule, str):
                raise SystemExit(
                    "negative typing check returned an unruled or unlocated diagnostic"
                )
            if diagnostic.get("severity") != "error":
                raise SystemExit("negative typing check returned a non-error diagnostic")
            filenames.append(diagnostic.get("file"))
            actual.append((line + 1, rule, str(diagnostic.get("message", ""))))
        expected_list = sorted((line, rule, "") for line, rule in expected)
        actual_keys = sorted((line, rule, "") for line, rule, _ in actual)
        if (
            result.returncode != 1
            or actual_keys != expected_list
            or report.get("summary", {}).get("errorCount") != len(expected)
        ):
            raise SystemExit(
                "negative typing check did not match its expected diagnostics:\n"
                f"expected={expected_list!r}\nactual={actual_keys!r}\n"
                f"{result.stdout}\n{result.stderr}"
            )
        if report.get("summary", {}).get("filesAnalyzed") != 1:
            raise SystemExit("negative typing check did not analyze exactly one fixture")
        if any(
            not isinstance(filename, str) or Path(filename).resolve() != fixture.resolve()
            for filename in filenames
        ):
            raise SystemExit("negative typing check returned a diagnostic outside its fixture")


def main() -> int:
    _check_positive()
    _check_negative()
    print("strict positive and negative typing checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
