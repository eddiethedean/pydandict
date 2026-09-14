"""Executable contracts for open Sol Phase 0.2 blockers.

These tests intentionally fail until the corresponding SOL findings are fixed.
Production implementation is unchanged by the review.
"""

import ast
import gc
import json
import subprocess
from collections.abc import MutableMapping, MutableSequence
from functools import cached_property
from pathlib import Path
from typing import Any, ForwardRef, Generic, TypeVar

import pytest
from pydantic import ConfigDict, Field, ValidationError, computed_field, model_validator

from pydandict import DictModel, _compat
from tools import benchmark, check_typing, qualify_package

ROOT = Path(__file__).resolve().parents[1]


def test_sol001_deferred_concrete_annotation_rejected_on_completion():
    class Deferred(DictModel):
        payload: ForwardRef("Later")

    with pytest.raises(TypeError, match=r"^pydandict_unsupported_annotation:.*MutableSequence"):
        Deferred.model_rebuild(_types_namespace={"Later": list[int]})
        Deferred(payload=[1])


def test_sol001_typed_extra_values_are_recursively_audited():
    with pytest.raises(TypeError, match=r"^pydandict_unsupported_annotation:.*MutableSequence"):

        class TypedExtra(DictModel):
            model_config = ConfigDict(extra="allow")
            __pydantic_extra__: dict[str, list[int]] = Field(init=False)

        TypedExtra(extra=[1])


def test_sol001_unbound_nested_generic_cannot_escape():
    value_type = TypeVar("value_type")

    class Box(DictModel, Generic[value_type]):
        payload: value_type

    class Envelope(DictModel):
        box: Box

    with pytest.raises(TypeError, match=r"^pydandict_unsupported_annotation:"):
        Envelope(box={"payload": [1]})


@pytest.mark.parametrize("position", ["key", "set", "frozenset"])
def test_sol002_models_in_hash_positions_rejected_without_committing(position):
    class Key(DictModel):
        model_config = ConfigDict(frozen=True)
        number: int

    class Broad(DictModel):
        payload: Any

    key = Key(number=1)
    value = {key: 1} if position == "key" else {key} if position == "set" else frozenset([key])
    model = Broad(payload=[1])
    old = model.payload
    before = model.model_dump_json(), model.model_fields_set
    with pytest.raises(TypeError, match=r"^pydandict_unsupported_value:"):
        model.payload = value
    assert (model.model_dump_json(), model.model_fields_set) == before
    assert model.payload is old
    model.payload.append(2)
    assert model.payload == [1, 2]


@pytest.mark.parametrize("slot", ["sequence", "mapping"])
def test_sol003_nested_model_identity_assignment_is_a_noop(slot):
    calls = []

    class Child(DictModel):
        number: int

    class Parent(DictModel):
        children: MutableSequence[Child]
        table: MutableMapping[str, Child]

        @model_validator(mode="after")
        def count(self):
            calls.append(1)
            return self

    model = Parent(children=[{"number": 1}], table={"first": {"number": 2}})
    container = model.children if slot == "sequence" else model.table
    key = 0 if slot == "sequence" else "first"
    child = container[key]
    iterator = iter(container)
    calls.clear()
    container[key] = child
    assert container[key] is child, "identity assignment replaced and staled the borrowed model"
    assert calls == [], "identity assignment reran root validation"
    expected = child if slot == "sequence" else "first"
    assert next(iterator) == expected


def test_sol003_model_identity_assignment_checks_frozen_ancestors():
    class Child(DictModel):
        numbers: MutableSequence[int]

    class FrozenParent(DictModel):
        model_config = ConfigDict(frozen=True)
        child: Child

    model = FrozenParent(child={"numbers": [1]})
    numbers = model.child.numbers
    with pytest.raises(ValidationError) as error:
        model.child.numbers = numbers
    assert error.value.errors()[0]["type"] == "frozen_instance"
    assert model.child.numbers is numbers


def test_sol004_rebuild_invalidates_compiled_alias_variants_before_first_instance():
    class Aliased(DictModel):
        number: int = Field(alias="input_number")

    with pytest.raises(ValidationError):
        Aliased.model_validate({"input_number": "bad"}, by_alias=True, by_name=True)
    previous = Aliased._entry_validator(True, True)
    previous_schema = Aliased.__pydantic_core_schema__
    assert Aliased.model_rebuild(force=True)
    assert Aliased.__pydantic_core_schema__ is not previous_schema
    assert Aliased._entry_validator(True, True) is not previous


def test_sol004_incompatible_schema_shape_fails_with_compatibility_diagnostic(monkeypatch):
    class Record(DictModel):
        number: int

    monkeypatch.setattr(Record, "__pydantic_core_schema__", None)
    with pytest.raises(TypeError, match=r"^pydandict_incompatible_pydantic:"):
        _compat.core_schema(Record)


def test_sol004_raw_storage_and_schema_operations_stay_in_compatibility_boundary():
    source = ROOT / "src" / "pydandict" / "_core.py"
    tree = ast.parse(source.read_text())
    violations = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id == "SchemaValidator":
            violations.append((node.lineno, "schema compilation"))
        if isinstance(node.func, ast.Attribute) and node.func.attr in (
            "__getattribute__",
            "__setattr__",
        ):
            if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
                name = node.args[1].value
                if isinstance(name, str) and (name == "__dict__" or name.startswith("__pydantic_")):
                    violations.append((node.lineno, name))
    assert not violations, f"version-sensitive operations bypass the adapter: {violations}"


def test_sol005_positive_gate_rejects_incomplete_source_coverage(monkeypatch):
    report = {"summary": {"filesAnalyzed": 2, "errorCount": 0}, "generalDiagnostics": []}
    result = subprocess.CompletedProcess([], 0, stdout=json.dumps(report), stderr="")
    monkeypatch.setattr(check_typing, "_run", lambda args: result)
    with pytest.raises(SystemExit):
        check_typing._check_positive()


@pytest.mark.parametrize("unexpected", ["duplicate", "unruled"])
def test_sol005_negative_gate_rejects_every_unexpected_diagnostic(monkeypatch, unexpected):
    expected = check_typing._expected_diagnostics(ROOT / "tests" / "typing_negative.py")
    diagnostics = [
        {"severity": "error", "rule": rule, "range": {"start": {"line": line - 1}}}
        for line, rule in sorted(expected)
    ]
    if unexpected == "duplicate":
        diagnostics.append(dict(diagnostics[0]))
    else:
        diagnostics.append(
            {"severity": "error", "message": "Expected expression", "range": {"start": {"line": 1}}}
        )
    report = {
        "summary": {"filesAnalyzed": 1, "errorCount": len(diagnostics)},
        "generalDiagnostics": diagnostics,
    }
    result = subprocess.CompletedProcess([], 1, stdout=json.dumps(report), stderr="")
    monkeypatch.setattr(check_typing, "_run", lambda args: result)
    with pytest.raises(SystemExit):
        check_typing._check_negative()


def test_sol006_qualification_installs_and_exercises_both_artifacts(monkeypatch):
    installs = []

    def fake_run(args, cwd, *, env=None):
        output = ""
        if "build" in args:
            directory = Path(args[args.index("--outdir") + 1])
            (directory / "pydandict.whl").write_bytes(b"review artifact")
            if "--sdist" in args:
                (directory / "pydandict.tar.gz").write_bytes(b"review sdist")
        if "pip" in args and "install" in args:
            installs.extend(Path(arg) for arg in args if arg.endswith(".whl"))
        if "-c" in args:
            site_packages = Path(cwd) / "venv" / "site-packages"
            (site_packages / "pydandict").mkdir(parents=True, exist_ok=True)
            (site_packages / "pydandict" / "py.typed").touch()
            output = str(site_packages)
        return subprocess.CompletedProcess(args, 0, stdout=output, stderr="")

    def fake_extract(archive, destination):
        destination.mkdir(parents=True)
        return destination

    monkeypatch.setattr(qualify_package, "run", fake_run)
    monkeypatch.setattr(qualify_package, "extract_sdist", fake_extract)
    monkeypatch.setattr(qualify_package.venv.EnvBuilder, "create", lambda self, path: None)
    assert qualify_package.main() == 0
    assert len(set(installs)) == 2, "rebuilt wheel was hashed but never installed or exercised"


def test_sol007_benchmark_records_the_required_source_baseline(capsys):
    assert benchmark.main() == 0
    report = json.loads(capsys.readouterr().out)
    serialized = json.dumps(report)
    assert "07fec9b" in serialized, (
        "benchmark baseline is a plain dict, not the approved source revision"
    )


def test_sol008_phase02_evidence_record_and_readable_findings_exist():
    research = ROOT / "docs" / "research"
    assert (research / "phase-0.2-results.json").is_file(), "required AC evidence record is missing"
    assert (research / "phase-0.2-findings.md").is_file(), (
        "required readable evidence report is missing"
    )


def test_sol009_discarded_cache_finalizes_after_all_swaps_while_root_is_busy():
    observations = []
    roots = []

    class Marker:
        def __del__(self):
            root = roots[0]
            observations.append((root.low, root.high, root._pd_busy))

    class Cached(DictModel):
        low: int
        high: int

        @computed_field
        @cached_property
        def marker(self) -> Any:
            return Marker()

    gc.collect()
    model = Cached(low=1, high=1)
    roots.append(model)
    model.marker
    model.update(low=2, high=3)
    gc.collect()
    assert observations == [(2, 3, True)], "old cache disposal escaped the guarded commit lifecycle"
