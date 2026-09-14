"""Independent release-contract verification for Phase 0.3 blockers only."""

import ast
import json
import subprocess
from datetime import date
from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError, create_model

from pydandict import DictModel
from tools import qualify_package

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("operation", ["update", "reset"])
def test_sol014_non_string_bulk_names_precede_frozen_policy(operation):
    class Record(DictModel):
        model_config = ConfigDict(extra="allow")
        fixed: int = Field(default=1, frozen=True)
        editable: int = 1

    record = Record()
    before = dict(record), tuple(record), record.model_fields_set
    with pytest.raises(TypeError, match="pydandict_protected_name"):
        if operation == "update":
            record.update({"fixed": 2, 1: 3})
        else:
            record.reset("fixed", 1)
    assert (dict(record), tuple(record), record.model_fields_set) == before
    record.editable = 2
    assert record.editable == 2


@pytest.mark.parametrize("kind", ["readable", "machine-readable"])
def test_sol015_phase03_has_fresh_qualification_records(kind):
    research = ROOT / "docs" / "research"
    if kind == "readable":
        assert (research / "phase-0.3-findings.md").is_file(), (
            "Phase 0.3 P5 requires fresh readable AC-linked qualification evidence"
        )
    else:
        # Internal result filenames are recommendations, not part of the API.
        records = list(research.glob("phase-0.3*.json"))
        assert records, "Phase 0.3 P5 requires fresh machine-readable qualification evidence"
        for path in records:
            assert isinstance(json.loads(path.read_text()), dict)


def test_sol016_qualification_executes_actual_example_against_both_bare_wheels(monkeypatch):
    """Check orchestration; actual example assertions must also pass in real runs."""
    example_source = (ROOT / "examples" / "library_config.py").read_text().strip()
    exercised = set()

    def source_in(argument):
        if len(argument) < 250 and "\n" not in argument:
            path = Path(argument)
            if path.is_file():
                return path.read_text().strip()
        return argument.strip()

    def fake_run(args, cwd, *, env=None):
        output = ""
        if "build" in args:
            directory = Path(args[args.index("--outdir") + 1])
            (directory / "pydandict.whl").write_bytes(b"review artifact")
            if "--sdist" in args:
                (directory / "pydandict.tar.gz").write_bytes(b"review sdist")
        if "-c" in args:
            site = Path(cwd) / "venv" / "site-packages"
            (site / "pydandict").mkdir(parents=True, exist_ok=True)
            (site / "pydandict" / "py.typed").touch()
            output = str(site)
        # Accept direct file execution, inline source or a runpy-style wrapper
        # referencing the actual example, without fixing its copied location.
        candidates = [source_in(argument) for argument in args[1:]]
        for source in tuple(candidates):
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    candidates.append(source_in(node.value))
        if any(example_source in candidate for candidate in candidates):
            assert env is not None and "PYTHONPATH" not in env
            assert not Path(cwd).resolve().is_relative_to(ROOT)
            exercised.add(Path(args[0]).parent.parent.name)
        return subprocess.CompletedProcess(args, 0, stdout=output, stderr="")

    def fake_extract(archive, destination):
        destination.mkdir(parents=True)
        return destination

    monkeypatch.setattr(qualify_package, "run", fake_run)
    monkeypatch.setattr(qualify_package, "extract_sdist", fake_extract)
    monkeypatch.setattr(qualify_package.venv.EnvBuilder, "create", lambda self, path: None)
    assert qualify_package.main() == 0
    assert {"direct-bare", "rebuilt-bare"} <= exercised, (
        "Required installed library-config example was not run against both bare wheel paths: "
        f"{exercised}"
    )


@pytest.mark.parametrize("mode", ["strings", "json"])
def test_sol017_strict_scalar_entry_modes_match_pinned_basemodel(mode):
    annotation = int if mode == "strings" else date
    record_type = create_model("Record", __base__=DictModel, value=(annotation, ...))
    control_type = create_model("Control", __base__=BaseModel, value=(annotation, ...))
    payload = {"value": "2"} if mode == "strings" else '{"value":"2026-01-01"}'
    method = f"model_validate_{mode}"
    expected = getattr(control_type, method)(payload, strict=True)
    actual = getattr(record_type, method)(payload, strict=True)
    assert actual.value == expected.value
    assert actual.model_fields_set == expected.model_fields_set == {"value"}
    # Keeping JSON/strings semantics must not relax strict Python validation.
    with pytest.raises(ValidationError):
        record_type.model_validate({"value": "2"}, strict=True)
