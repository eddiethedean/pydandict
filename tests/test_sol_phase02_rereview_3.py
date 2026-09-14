"""Sol contracts for remaining blockers in the third Phase 0.2 re-review."""

import json
from pathlib import Path
from typing import ClassVar

import pytest

from pydandict import DictModel

ROOT = Path(__file__).resolve().parents[1]


def test_sol001_unresolved_ignored_classvar_cannot_bypass_deferred_field_audit():
    ignored_annotation = "NotDefined"

    class Child(DictModel):
        ignored: ClassVar[ignored_annotation]
        numbers: "Later"

    Later = list[int]

    class Parent(DictModel):
        child: Child

    with pytest.raises(TypeError, match=r"^pydandict_unsupported_annotation:"):
        Parent(child={"numbers": [1]})
    assert Later == list[int]


def test_sol008_final_benchmark_identifies_the_qualified_candidate_source():
    record = json.loads((ROOT / "docs/research/phase-0.2-results.json").read_text())
    assert record["benchmark"]["sources"]["candidate"]["hashes"] == record["source"]["hashes"], (
        "the designated final benchmark describes a different implementation; "
        "preserve old measurements as history and record actual candidate measurements"
    )
