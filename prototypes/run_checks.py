"""Build, exercise and record the prototype without publishing or contacting people."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from importlib.metadata import version

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
REPORT = REPO / "docs" / "research" / "prototype-results.json"


def run(command, *, cwd=ROOT, env=None, expected=0):
    result = subprocess.run(
        [str(v) for v in command], cwd=cwd, env=env, capture_output=True, text=True
    )
    if result.returncode != expected:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"command failed ({result.returncode}): {command}")
    return result.stdout.strip()


def main():
    source_env = dict(
        os.environ, PYTHONPATH=str(ROOT), PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"
    )
    clean_env = dict(os.environ)
    clean_env.pop("PYTHONPATH", None)
    sources = sorted(
        p
        for p in ROOT.rglob("*")
        if p.is_file()
        and p.suffix in {".py", ".toml", ".txt"}
        and not {"build", "dist", "__pycache__", ".egg-info"} & set(p.parts)
        and not any(x.endswith(".egg-info") for x in p.parts)
    )
    hashes = {
        str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sources
    }
    report = {
        "scope": "Integrated prototype evidence, not a supported package release",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "base_commit": run(["git", "rev-parse", "HEAD"]),
        "source_sha256": hashes,
        "versions": {
            name: version(name)
            for name in (
                "pydantic",
                "pydantic-core",
                "fastapi",
                "starlette",
                "httpx",
                "pyright",
                "pytest",
                "hypothesis",
                "build",
                "setuptools",
            )
        },
        "commands": [],
    }
    with tempfile.TemporaryDirectory(prefix="pydandict-qualification-") as directory:
        temp = Path(directory)
        print("Running runtime and stateful tests...", flush=True)
        junit = temp / "tests.xml"
        report["tests_output"] = run(
            [
                sys.executable,
                "-m",
                "pytest",
                ROOT / "tests",
                "-q",
                f"--junitxml={junit}",
            ],
            env=source_env,
        )
        suites = ET.parse(junit).getroot()
        report["tests"] = {
            key: sum(int(s.attrib.get(key, 0)) for s in suites.iter("testsuite"))
            for key in ("tests", "failures", "errors", "skipped")
        }
        report["commands"].append(
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=prototypes python -m pytest prototypes/tests -q"
        )
        report["strategies"] = json.loads(
            run([sys.executable, ROOT / "compare_strategies.py"], env=source_env)
        )
        report["benchmarks"] = json.loads(
            run([sys.executable, ROOT / "benchmark.py"], env=source_env)
        )
        print("Building wheel and sdist...", flush=True)
        dist = ROOT / "dist"
        run([sys.executable, "-m", "build", ROOT, "--outdir", dist])
        wheel = dist / "pydandict_prototype-0.1.0.dev0-py3-none-any.whl"
        sdist = dist / "pydandict_prototype-0.1.0.dev0.tar.gz"
        with zipfile.ZipFile(wheel) as archive:
            names = archive.namelist()
            assert "pydandict_prototype/py.typed" in names
            assert not any(".venv" in n or "__pycache__" in n for n in names)
        unpacked = temp / "sdist"
        with tarfile.open(sdist) as archive:
            archive.extractall(unpacked, filter="data")
        run(
            [
                sys.executable,
                "-m",
                "build",
                unpacked / "pydandict_prototype-0.1.0.dev0",
                "--wheel",
                "--outdir",
                dist / "from-sdist",
            ]
        )
        rebuilt = dist / "from-sdist" / wheel.name
        report["artifacts"] = {
            str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (wheel, sdist, rebuilt)
        }
        report["commands"].append(
            "python -m build prototypes; rebuild wheel from the extracted sdist"
        )
        print("Running isolated wheel consumers and installed typing...", flush=True)
        report["consumers"] = {}
        for name, artifact in [("library", wheel), ("fastapi", rebuilt)]:
            project = temp / name
            project.mkdir()
            run(["uv", "venv", "--python", sys.executable, project / ".venv"])
            python = project / ".venv" / "bin" / "python"
            run(
                [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    python,
                    artifact,
                    "fastapi==0.141.1",
                    "httpx==0.28.1",
                    "pyright==1.1.411",
                ]
            )
            script = ROOT / "consumers" / f"{name}_consumer.py"
            shutil.copy2(script, project / script.name)
            report["consumers"][name] = run(
                [python, project / script.name], cwd=project, env=clean_env
            )
            imported = run(
                [
                    python,
                    "-c",
                    "import pydandict_prototype; print(pydandict_prototype.__file__)",
                ],
                cwd=project,
                env=clean_env,
            )
            assert str(project / ".venv") in imported
            if name == "library":
                # Resolve the installed artifact explicitly for Pyright verifytypes.
                type_env = dict(clean_env, PYTHONPATH=str(Path(imported).parent.parent))
                for filename in ("typing_positive.py", "typing_negative.py"):
                    shutil.copy2(ROOT / "consumers" / filename, project / filename)
                report["typing_positive"] = json.loads(
                    run(
                        [
                            python,
                            "-m",
                            "pyright",
                            "typing_positive.py",
                            "--outputjson",
                            "--pythonpath",
                            python,
                        ],
                        cwd=project,
                        env=type_env,
                    )
                )["summary"]
                negative = json.loads(
                    run(
                        [
                            python,
                            "-m",
                            "pyright",
                            "typing_negative.py",
                            "--outputjson",
                            "--pythonpath",
                            python,
                        ],
                        cwd=project,
                        env=type_env,
                        expected=1,
                    )
                )
                actual = {
                    (d["range"]["start"]["line"] + 1, d["rule"])
                    for d in negative["generalDiagnostics"]
                }
                expected = {
                    (i, line.split("# expected: ")[1])
                    for i, line in enumerate(
                        (project / "typing_negative.py").read_text().splitlines(), 1
                    )
                    if "# expected: " in line
                }
                assert actual == expected, (actual, expected)
                report["typing_negative"] = {
                    "diagnostics_matched": len(actual),
                    "unexpected": 0,
                }
                completeness = json.loads(
                    run(
                        [
                            python,
                            "-m",
                            "pyright",
                            "--verifytypes",
                            "pydandict_prototype",
                            "--ignoreexternal",
                            "--outputjson",
                            "--pythonpath",
                            python,
                        ],
                        cwd=project,
                        env=type_env,
                    )
                )
                assert (
                    str(project / ".venv")
                    in completeness["typeCompleteness"]["packageRootDirectory"]
                )
                assert completeness["typeCompleteness"]["completenessScore"] == 1
                report["type_completeness"] = completeness["typeCompleteness"][
                    "completenessScore"
                ]
        report["commands"].append(
            "Install each wheel into a separate clean environment; run library/HTTP consumers and positive/negative Pyright fixtures outside the checkout"
        )
    REPORT.write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"Passed: {report['tests']}; public type completeness 100%; both artifact consumers passed."
    )
    print(f"Evidence: {REPORT}")


if __name__ == "__main__":
    main()
