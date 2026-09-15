"""Execute every Python fenced block in the public Markdown documentation."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def python_blocks(path: Path) -> list[tuple[int, str]]:
    lines = path.read_text().splitlines()
    blocks: list[tuple[int, str]] = []
    fence: str | None = None
    code: list[str] = []
    start = 0
    for number, line in enumerate(lines, 1):
        if line.startswith("```"):
            language = line[3:].strip()
            if fence is None:
                fence = language
                code = []
                start = number + 1
            else:
                if fence == "python":
                    blocks.append((start, "\n".join(code)))
                fence = None
            continue
        if fence is not None:
            code.append(line)
    if fence is not None:
        raise ValueError(f"{path.relative_to(ROOT)} has an unclosed code fence")
    return blocks


def main() -> int:
    paths = [*sorted(ROOT.glob("*.md")), *sorted((ROOT / "docs").rglob("*.md"))]
    examples = [(path, line, code) for path in paths for line, code in python_blocks(path)]
    environment = os.environ.copy()
    source_path = str(ROOT / "src")
    environment["PYTHONPATH"] = os.pathsep.join(
        part for part in (source_path, environment.get("PYTHONPATH", "")) if part
    )
    environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    for path, line, code in examples:
        label = f"{path.relative_to(ROOT)}:{line}"
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode:
            print(f"FAIL {label}", file=sys.stderr)
            if result.stdout:
                print(result.stdout, file=sys.stderr, end="")
            if result.stderr:
                print(result.stderr, file=sys.stderr, end="")
            return result.returncode
        if not result.stdout.strip():
            print(f"FAIL {label}: example must print its observed output", file=sys.stderr)
            return 1
        print(f"PASS {label}: {result.stdout.strip().replace(chr(10), ' | ')}")

    print(f"Executed {len(examples)} Python documentation examples: 0 failures.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
