"""Sol verification contracts for blockers in the second Phase 0.2 re-review."""

import ast
import hashlib
import json
from collections.abc import MutableSequence
from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from pydandict import DictModel

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("storage", ["field", "typed_extra"])
def test_sol001_deferred_nested_abc_migration_remains_supported(storage):
    if storage == "field":

        class Child(DictModel):
            numbers: "Later"

    else:

        class Child(DictModel):
            model_config = ConfigDict(extra="allow")
            __pydantic_extra__: dict[str, "Later"] = Field(init=False)

    Later = MutableSequence[int]

    class Parent(DictModel):
        child: Child

    parent = Parent(child={"numbers": [1]})
    numbers = parent.child["numbers"]
    assert isinstance(numbers, MutableSequence)
    numbers.append("2")
    assert parent.model_dump() == {"child": {"numbers": [1, 2]}}
    assert parent.child["numbers"] is numbers
    assert Later == MutableSequence[int]


def test_sol004_core_schema_access_including_getattr_stays_in_adapter():
    violations = []
    for source in (ROOT / "src" / "pydandict").glob("*.py"):
        if source.name == "_compat.py":
            continue
        for node in ast.walk(ast.parse(source.read_text())):
            direct = isinstance(node, ast.Attribute) and node.attr == "__pydantic_core_schema__"
            reflected = (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "getattr"
                and len(node.args) > 1
                and isinstance(node.args[1], ast.Constant)
                and node.args[1].value == "__pydantic_core_schema__"
            )
            if direct or reflected:
                violations.append((source.name, node.lineno))
    assert not violations, f"unchecked core-schema access outside adapter: {violations}"


def test_sol008_final_evidence_identifies_measured_source_and_candidate_ci():
    record = json.loads((ROOT / "docs/research/phase-0.2-results.json").read_text())
    actual = {
        path.relative_to(ROOT / "src").as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (ROOT / "src/pydandict").iterdir()
        if path.is_file() and (path.suffix == ".py" or path.name == "py.typed")
    }
    problems = []
    if record["source"]["hashes"] != actual:
        problems.append("final evidence source hashes do not identify the current implementation")
    if not record["ci"]["current_candidate_run"]:
        problems.append("final evidence has no current candidate CI result")
    assert not problems, "; ".join(problems)


def test_sol013_existing_model_validation_produces_independent_owned_result():
    class Control(BaseModel):
        model_config = ConfigDict(revalidate_instances="always")
        numbers: list[int]

    class Record(DictModel):
        numbers: MutableSequence[int]

    control = Control(numbers=[1])
    assert Control.model_validate(control, strict=True) is not control
    original = Record(numbers=[1])
    numbers = original.numbers
    iterator = iter(numbers)
    validated = Record.model_validate(original, strict=True, context={"request": 1})

    assert validated is not original, "public validation committed into its input root"
    assert original.numbers is numbers
    validated.numbers.append(2)
    assert validated.model_dump() == {"numbers": [1, 2]}
    assert original.model_dump() == {"numbers": [1]}
    assert next(iterator) == 1
    numbers.append(3)
    assert original.numbers == [1, 3] and validated.numbers == [1, 2]


def test_sol013_failed_public_validation_does_not_mutate_existing_input():
    class Record(DictModel):
        numbers: MutableSequence[int]

        @field_validator("numbers", mode="before")
        @classmethod
        def normalize_candidate(cls, value, info):
            # Deterministic and idempotent normalization of request input, followed
            # by an ordinary validation failure. Canonical context=None is valid.
            if info.context:
                if 2 not in value:
                    value.append(2)
                raise ValueError("later validation failure")
            return value

    original = Record(numbers=[1])
    numbers = original.numbers
    iterator = iter(numbers)
    before = original.model_dump(), original.model_fields_set
    with pytest.raises(ValidationError, match="later validation failure"):
        Record.model_validate(original, context={"request": 1})

    assert (original.model_dump(), original.model_fields_set) == before
    assert original.numbers is numbers
    assert next(iterator) == 1
    numbers.append(3)
    assert original.numbers == [1, 3]
