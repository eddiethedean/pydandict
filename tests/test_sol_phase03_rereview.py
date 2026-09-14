"""Independent verification of unresolved Phase 0.3 release blockers only."""

import json
import subprocess
from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator, model_validator

from pydandict import DictModel
from tools import qualify_package


@pytest.mark.parametrize("option", ["strict", "extra", "context"])
def test_sol017_json_entry_options_match_pinned_basemodel(option):
    class Control(BaseModel):
        model_config = ConfigDict(extra="allow")
        value: int

        @field_validator("value")
        @classmethod
        def contextual_value(cls, value, info):
            return value * (info.context or {}).get("factor", 1)

    class Record(DictModel):
        model_config = ConfigDict(extra="allow")
        value: int

        @field_validator("value")
        @classmethod
        def contextual_value(cls, value, info):
            return value * (info.context or {}).get("factor", 1)

    if option == "context":
        payload = '{"value":2}'
        expected = Control.model_validate_json(payload, context={"factor": 3})
        actual = Record.model_validate_json(payload, context={"factor": 3})
        assert actual.value == expected.value == 6
    elif option == "strict":
        payload = '{"value":"2"}'
        with pytest.raises(ValidationError):
            Control.model_validate_json(payload, strict=True)
        with pytest.raises(ValidationError):
            Record.model_validate_json(payload, strict=True)
    else:
        payload = '{"value":2,"other":3}'
        with pytest.raises(ValidationError):
            Control.model_validate_json(payload, extra="forbid")
        with pytest.raises(ValidationError):
            Record.model_validate_json(payload, extra="forbid")


def test_sol017_rejected_strings_callback_cannot_mutate_entry_source():
    class Record(DictModel):
        value: int

        @model_validator(mode="before")
        @classmethod
        def reject_after_edit(cls, value):
            value["value"] = "9"
            raise ValueError("rejected after edit")

    source = {"value": "2"}
    with pytest.raises(ValidationError):
        Record.model_validate_strings(source)
    assert source == {"value": "2"}, "Public validation must detach before user callbacks"


def test_sol015_missing_provenance_cannot_replace_durable_evidence(monkeypatch, tmp_path):
    """Simulate successful commands without a source identity in an isolated root."""
    original_root = qualify_package.ROOT
    for relative in ("examples/library_config.py", "tests/typing_negative.py"):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((original_root / relative).read_text())
    research = tmp_path / "docs" / "research"
    research.mkdir(parents=True)
    record = research / "phase-0.3-results.json"
    original = json.dumps({"source_commit": "a" * 40, "prior_verified_record": True})
    record.write_text(original)

    def fake_run(args, cwd, *, env=None):
        output = ""
        if "build" in args:
            directory = Path(args[args.index("--outdir") + 1])
            (directory / "pydandict.whl").write_bytes(b"simulated artifact")
            if "--sdist" in args:
                (directory / "pydandict.tar.gz").write_bytes(b"simulated sdist")
        if "-c" in args:
            site = Path(cwd) / "venv" / "site-packages"
            (site / "pydandict").mkdir(parents=True, exist_ok=True)
            (site / "pydandict" / "py.typed").touch()
            output = str(site)
        return subprocess.CompletedProcess(args, 0, stdout=output, stderr="")

    def fake_extract(archive, destination):
        destination.mkdir(parents=True)
        return destination

    monkeypatch.setattr(qualify_package, "ROOT", tmp_path)
    monkeypatch.setattr(qualify_package, "run", fake_run)
    monkeypatch.setattr(qualify_package, "extract_sdist", fake_extract)
    monkeypatch.setattr(qualify_package.venv.EnvBuilder, "create", lambda self, path: None)
    try:
        qualify_package.main()
    except RuntimeError:
        pass
    assert record.read_text() == original, (
        "Qualification without a valid source identity replaced durable verified evidence"
    )
