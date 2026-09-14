"""Build and exercise release artifacts from clean external environments."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import venv
from pathlib import Path

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
        direct = work / "direct"
        direct.mkdir()
        run([sys.executable, "-m", "build", "--sdist", "--wheel", "--outdir", str(direct)], ROOT)
        run([sys.executable, "-m", "twine", "check", *map(str, direct.iterdir())], ROOT)
        sdist = next(direct.glob("*.tar.gz"), None)
        if sdist is None:
            raise RuntimeError("build did not produce an sdist")
        source = extract_sdist(sdist, work / "source")
        rebuilt = work / "rebuilt"
        rebuilt.mkdir()
        run([sys.executable, "-m", "build", "--wheel", "--outdir", str(rebuilt)], source)
        wheel = next(direct.glob("*.whl"))
        rebuilt_wheel = next(rebuilt.glob("*.whl"))
        hashes = {
            "direct_wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
            "rebuilt_wheel_sha256": hashlib.sha256(rebuilt_wheel.read_bytes()).hexdigest(),
            "direct_wheel": wheel.name,
            "rebuilt_wheel": rebuilt_wheel.name,
        }

        environment = work / "venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(environment)
        isolated_python = python_in(environment)
        run(
            [
                str(isolated_python),
                "-m",
                "pip",
                "install",
                str(wheel),
                "fastapi==0.141.1",
                "httpx==0.28.1",
                "pyright==1.1.411",
            ],
            work,
        )
        consumer = work / "consumer.py"
        consumer.write_text(
            "from fastapi import FastAPI\n"
            "from fastapi.testclient import TestClient\n"
            "from pydandict import DictModel\n"
            "class Item(DictModel):\n"
            "    value: int\n"
            "app = FastAPI()\n"
            "@app.get('/item', response_model=Item)\n"
            "def item() -> Item: return Item(value=3)\n"
            "response = TestClient(app).get('/item')\n"
            "assert response.status_code == 200 and response.json() == {'value': 3}\n"
        )
        typing_consumer = work / "typing_consumer.py"
        typing_consumer.write_text(
            "from collections.abc import Mapping\n"
            "from pathlib import Path\n"
            "from typing import assert_type\n"
            "from pydandict import DictModel\n"
            "class Item(DictModel):\n"
            "    value: int\n"
            "item = Item(value=3)\n"
            "assert_type(item.value, int)\n"
            "mapping: Mapping[str, object] = item\n"
            "module = Path(__import__('pydandict').__file__).resolve()\n"
            f"assert {str(ROOT)!r} not in str(module)\n"
        )
        clean_env = dict(os.environ)
        clean_env.pop("PYTHONPATH", None)
        run([str(isolated_python), str(consumer)], work, env=clean_env)
        pyright_config = work / "pyrightconfig.json"
        site_packages = Path(
            run(
                [str(isolated_python), "-c", "import site; print(site.getsitepackages()[0])"],
                work,
                env=clean_env,
            ).stdout.strip()
        )
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
        run(
            [str(isolated_python), "-m", "pyright", "--project", str(pyright_config)],
            work,
            env=clean_env,
        )
        if not (site_packages / "pydandict" / "py.typed").is_file():
            raise RuntimeError("installed artifact is missing its py.typed marker")
        print(json.dumps(hashes, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
