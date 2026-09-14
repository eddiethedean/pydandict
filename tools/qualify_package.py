"""Build and exercise release artifacts from clean external environments."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import tarfile
import tempfile
import venv
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]


def run(
    args: list[str], cwd: Path, *, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f"command failed ({' '.join(args)}):\n{result.stdout}\n{result.stderr}")
    return result


def python_in(venv_dir: Path) -> Path:
    relative = Path("Scripts/python.exe") if os.name == "nt" else Path("bin/python")
    return venv_dir / relative


def extract_sdist(archive: Path, destination: Path) -> Path:
    with tarfile.open(archive) as handle:
        try:
            handle.extractall(destination, filter="data")
        except TypeError:  # Python 3.11 has no extraction filter argument.
            handle.extractall(destination)
    roots = [path for path in destination.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise RuntimeError("sdist did not contain exactly one project root")
    return roots[0]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="pydandict-qualification-") as temporary:
        work = Path(temporary)
        commands: list[dict[str, object]] = []

        def execute(
            args: list[str], cwd: Path, *, env: dict[str, str] | None = None
        ) -> subprocess.CompletedProcess[str]:
            commands.append({"argv": args, "cwd": str(cwd), "source_path_injection": False})
            return run(args, cwd, env=env)

        direct = work / "direct"
        direct.mkdir()
        execute(
            [sys.executable, "-m", "build", "--sdist", "--wheel", "--outdir", str(direct)], ROOT
        )
        execute([sys.executable, "-m", "twine", "check", *map(str, direct.iterdir())], ROOT)
        sdist = next(direct.glob("*.tar.gz"), None)
        if sdist is None:
            raise RuntimeError("build did not produce an sdist")
        source = extract_sdist(sdist, work / "source")
        rebuilt = work / "rebuilt"
        rebuilt.mkdir()
        execute([sys.executable, "-m", "build", "--wheel", "--outdir", str(rebuilt)], source)
        wheel = next(direct.glob("*.whl"))
        rebuilt_wheel = next(rebuilt.glob("*.whl"))
        hashes: dict[str, object] = {
            "sdist_sha256": hashlib.sha256(sdist.read_bytes()).hexdigest(),
            "sdist": sdist.name,
            "python": sys.version,
            "platform": platform.platform(),
            "direct_wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
            "rebuilt_wheel_sha256": hashlib.sha256(rebuilt_wheel.read_bytes()).hexdigest(),
            "direct_wheel": wheel.name,
            "rebuilt_wheel": rebuilt_wheel.name,
        }

        clean_env = dict(os.environ)
        clean_env.pop("PYTHONPATH", None)
        dependency_records: dict[str, str] = {}

        def exercise(artifact: Path, label: str) -> None:
            bare = work / f"{label}-bare"
            # Match the venv CLI defaults: managed POSIX interpreters may need
            # their original location to resolve shared libraries.
            venv.EnvBuilder(with_pip=True, clear=True, symlinks=os.name != "nt").create(bare)
            bare_python = python_in(bare)
            execute([str(bare_python), "-m", "pip", "install", str(artifact)], work, env=clean_env)
            bare_consumer = (
                "from pathlib import Path\n"
                "from collections.abc import Mapping, MutableSequence\n"
                "import sys, pydandict\n"
                "from pydantic import BaseModel, ValidationError\n"
                "from pydandict import DictModel\n"
                "module = Path(pydandict.__file__).resolve()\n"
                "assert module.is_relative_to(Path(sys.prefix).resolve())\n"
                f"assert not module.is_relative_to(Path({str(ROOT)!r}).resolve())\n"
                "class Item(DictModel):\n"
                "    numbers: MutableSequence[int]\n"
                "item = Item(numbers=[1])\n"
                "assert isinstance(item, BaseModel) and isinstance(item, Mapping)\n"
                "handle = item.numbers\n"
                "item.numbers.append(2)\n"
                "assert item.numbers is handle and item.model_dump() == {'numbers': [1, 2]}\n"
                "try:\n"
                "    item.numbers.append('bad')\n"
                "except ValidationError:\n"
                "    assert item.numbers == [1, 2]\n"
                "else:\n"
                "    raise AssertionError('invalid library edit committed')\n"
                "print(module)\n"
            )
            dependency_records[f"{label}_bare_import"] = execute(
                [str(bare_python), "-c", bare_consumer], work, env=clean_env
            ).stdout
            dependency_records[f"{label}_bare"] = execute(
                [str(bare_python), "-m", "pip", "freeze"], work, env=clean_env
            ).stdout

            environment = work / f"{label}-http"
            venv.EnvBuilder(with_pip=True, clear=True, symlinks=os.name != "nt").create(environment)
            isolated_python = python_in(environment)
            execute(
                [
                    str(isolated_python),
                    "-m",
                    "pip",
                    "install",
                    str(artifact),
                    "fastapi==0.141.1",
                    "httpx==0.28.1",
                    "pyright==1.1.411",
                ],
                work,
                env=clean_env,
            )
            consumer = work / f"{label}-consumer.py"
            consumer.write_text(
                "from fastapi import FastAPI\n"
                "from fastapi.testclient import TestClient\n"
                "from pydandict import DictModel\n"
                "class Item(DictModel):\n"
                "    value: int\n"
                "app = FastAPI()\n"
                "@app.post('/item', response_model=Item)\n"
                "def item(body: Item) -> Item: return body\n"
                "client = TestClient(app)\n"
                "response = client.post('/item', json={'value': 3})\n"
                "assert response.status_code == 200 and response.json() == {'value': 3}\n"
                "assert client.post('/item', json={'value': 'bad'}).status_code == 422\n"
                "assert 'Item' in client.get('/openapi.json').text\n"
            )
            typing_consumer = work / f"{label}-typing.py"
            typing_consumer.write_text(
                "from collections.abc import Mapping\n"
                "from pathlib import Path\n"
                "import sys\n"
                "from typing import assert_type\n"
                "from pydandict import DictModel\n"
                "class Item(DictModel):\n"
                "    value: int\n"
                "item = Item(value=3)\n"
                "assert_type(item.value, int)\n"
                "mapping: Mapping[str, object] = item\n"
                "module = Path(__import__('pydandict').__file__).resolve()\n"
                f"assert {str(ROOT)!r} not in str(module)\n"
                "assert module.is_relative_to(Path(sys.prefix).resolve())\n"
            )
            execute([str(isolated_python), str(consumer)], work, env=clean_env)
            execute([str(isolated_python), str(typing_consumer)], work, env=clean_env)
            site_packages = Path(
                execute(
                    [str(isolated_python), "-c", "import site; print(site.getsitepackages()[0])"],
                    work,
                    env=clean_env,
                ).stdout.strip()
            )
            if not (site_packages / "pydandict" / "py.typed").is_file():
                raise RuntimeError("installed artifact is missing its py.typed marker")
            pyright_config = work / f"{label}-pyrightconfig.json"
            pyright_config.write_text(
                json.dumps(
                    {
                        "include": [typing_consumer.name],
                        "extraPaths": [str(site_packages)],
                        "venvPath": str(work),
                        "venv": environment.name,
                        "typeCheckingMode": "strict",
                    }
                )
            )
            execute(
                [str(isolated_python), "-m", "pyright", "--project", str(pyright_config)],
                work,
                env=clean_env,
            )
            execute(
                [
                    str(isolated_python),
                    "-m",
                    "pyright",
                    "--verifytypes",
                    "pydandict",
                    "--ignoreexternal",
                ],
                work,
                env=clean_env,
            )
            negative = work / f"{label}-negative.py"
            negative.write_text((ROOT / "tests" / "typing_negative.py").read_text())
            negative_config = work / f"{label}-negative-config.json"
            negative_config.write_text(
                json.dumps(
                    {
                        "include": [negative.name],
                        "extraPaths": [str(site_packages)],
                        "typeCheckingMode": "strict",
                    }
                )
            )
            expected_errors: list[tuple[int, str]] = []
            for line, text in enumerate(negative.read_text().splitlines(), 1):
                if "# expected:" in text:
                    expected_errors.append((line, text.split("# expected:", 1)[1].strip()))
            # The driver treats the checker's exact expected failure as a successful
            # qualification command; execution always goes through the same runner.
            negative_driver = (
                dedent(
                    """
                import json, subprocess, sys
                from pathlib import Path
                fixture = Path(FIXTURE)
                expected = sorted(EXPECTED)
                result = subprocess.run(
                    [sys.executable, "-m", "pyright", "--project", CONFIG, "--outputjson"],
                    text=True, capture_output=True, check=False,
                )
                assert result.returncode == 1, result.stdout + result.stderr
                report = json.loads(result.stdout)
                diagnostics = report["generalDiagnostics"]
                actual = []
                for diagnostic in diagnostics:
                    assert diagnostic["severity"] == "error", diagnostic
                    assert Path(diagnostic["file"]).resolve() == fixture.resolve(), diagnostic
                    actual.append((diagnostic["range"]["start"]["line"] + 1, diagnostic["rule"]))
                assert sorted(actual) == expected, (actual, expected)
                assert report["summary"]["errorCount"] == len(expected), report
                assert report["summary"]["filesAnalyzed"] == 1, report
                print(json.dumps({"expected_errors": len(expected), "actual_errors": len(actual)}))
                """
                )
                .replace("FIXTURE", repr(str(negative)))
                .replace("EXPECTED", repr(expected_errors))
                .replace("CONFIG", repr(str(negative_config)))
            )
            dependency_records[f"{label}_negative_typing"] = execute(
                [str(isolated_python), "-c", negative_driver], work, env=clean_env
            ).stdout
            dependency_records[label] = execute(
                [str(isolated_python), "-m", "pip", "freeze"], work, env=clean_env
            ).stdout

        exercise(wheel, "direct")
        exercise(rebuilt_wheel, "rebuilt")
        hashes["resolved_dependencies"] = dependency_records
        hashes["commands"] = commands
        for label, artifact in (("direct", wheel), ("rebuilt", rebuilt_wheel)):
            if not artifact.is_file():
                raise RuntimeError(f"{label} artifact disappeared during qualification")
        print(json.dumps(hashes, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
