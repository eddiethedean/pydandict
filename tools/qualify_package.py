"""Build and exercise release artifacts from clean external environments."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tarfile
import tempfile
import venv
from pathlib import Path
from textwrap import dedent
from typing import cast

ROOT = Path(__file__).resolve().parents[1]
_COMMIT = re.compile(r"[0-9a-f]{40}")
_SCALAR_PROFILE = {
    "test": "tests/test_stateful.py::TestScalarTransactions",
    "max_examples": 100,
    "stateful_step_count": 100,
    "deadline": None,
    "derandomize": True,
    "status": "executed by the repository runtime/CI gate, not this artifact driver",
}
_RUNTIME_LANE = {
    "name": "CI compatibility matrix",
    "execution": "required external runtime gate; recorded separately from this artifact driver",
}
_ARTIFACT_LANE = {
    "name": "local package qualification",
    "execution": "executed by this driver for the recorded source/artifacts",
}
_DOCS_LANE = {"name": "Documentation checks", "execution": "required external docs gate"}
_MATRIX_CELLS = {
    **{
        f"runtime/{system}/{version}": "runtime"
        for system, versions in (
            ("ubuntu", ("3.11", "3.12", "3.13", "3.14")),
            ("macos", ("3.11", "3.14")),
            ("windows", ("3.11", "3.14")),
        )
        for version in versions
    },
    "artifact/ubuntu/3.11": "artifact",
    "artifact/ubuntu/3.14": "artifact",
    "docs/ubuntu/3.11": "docs",
}


def _coverage(
    *tests: str, lanes: tuple[dict[str, str], ...] = (_RUNTIME_LANE,)
) -> dict[str, object]:
    """Describe actual proof nodes without claiming this driver ran external gates."""
    applicable = {
        "CI compatibility matrix": "runtime",
        "local package qualification": "artifact",
        "Documentation checks": "docs",
    }
    kinds = {applicable[lane["name"]] for lane in lanes}
    return {
        "tests": list(tests),
        "lanes": [dict(lane) for lane in lanes],
        "matrix_cells": {
            cell: {
                "status": "required-external-execution" if kind in kinds else "non-applicable",
                "reason": (
                    "Execution must be reconciled to an actual source-qualified run."
                    if kind in kinds
                    else f"This criterion's proof is not executed by the {kind} job."
                ),
            }
            for cell, kind in _MATRIX_CELLS.items()
        },
    }


_AC_TEST_LANE_MAP = {
    "AC-001": _coverage(
        "tests/test_sol_phase03_blockers.py::test_sol017_strict_scalar_entry_modes_match_pinned_basemodel",
        "tests/test_sol_phase03_rereview_2.py::test_sol017_type_adapter_strict_json_matches_pinned_basemodel",
        "tests/test_sol_phase03_rereview_3.py::test_sol017_type_adapter_strict_strings_matches_pinned_basemodel",
        "tests/test_sol_phase03_rereview_3.py::test_sol017_type_adapter_json_preserves_field_specific_strictness",
        "tests/test_compat_remediation.py::test_public_validation_completes_deferred_schemas_before_adapter_access",
    ),
    "AC-002": _coverage(
        "tests/test_phase02_contract.py::test_concrete_mutable_annotations_fail_with_migration_hint",
        "tests/test_hash_ingress.py::test_unhashable_model_members_get_the_ownership_diagnostic",
    ),
    "AC-003": _coverage(
        "tests/test_phase03_contract.py::test_scalar_reads_views_and_canonical_namespace"
    ),
    "AC-004": _coverage(
        "tests/test_phase03_contract.py::test_scalar_reads_views_and_canonical_namespace"
    ),
    "AC-005": _coverage(
        "tests/test_phase03_evidence_contract.py::test_scalar_iterator_structure_and_exhaustion_contract"
    ),
    "AC-006": _coverage(
        "tests/test_inventory.py::test_explicit_public_alias_flags",
        "tests/test_inventory.py::test_alias_choices_paths_typed_extras_and_properties",
        "tests/test_prototype.py::test_properties_do_not_shadow_extra_mapping_state",
    ),
    "AC-007": _coverage(
        "tests/test_phase03_contract.py::test_scalar_bulk_failure_is_atomic_and_reset_updates_metadata",
        "tests/test_prototype.py::test_coupled_updates_rollback_aliases_and_defaults",
        "tests/test_stateful.py::TestScalarTransactions",
    ),
    "AC-008": _coverage(
        "tests/test_stateful.py::TestScalarTransactions",
        "tests/test_prototype.py::test_coupled_updates_rollback_aliases_and_defaults",
    ),
    "AC-009": _coverage(
        "tests/test_phase03_contract.py::test_non_string_pop_is_rejected_before_fallback",
        "tests/test_sol_phase03_blockers.py::test_sol014_non_string_bulk_names_precede_frozen_policy",
        "tests/test_prototype.py::test_late_generator_and_reentrancy_recover",
        "tests/test_sol_phase02_rereview.py::test_sol010_input_callbacks_run_under_the_same_root_guard",
    ),
    "AC-010": _coverage(
        "tests/test_stateful.py::TestScalarTransactions",
        "tests/test_prototype.py::test_extras_destructive_metadata_and_errors",
        "tests/test_inventory.py::test_alias_choices_paths_typed_extras_and_properties",
    ),
    "AC-011": _coverage("tests/test_prototype.py::test_extras_destructive_metadata_and_errors"),
    "AC-012": _coverage(
        "tests/test_stateful.py::TestScalarTransactions",
        "tests/test_inventory.py::test_nested_aliases_and_data_dependent_reset",
        "tests/test_inventory.py::test_shape_changing_validator_rejected_and_factory_failure_recovers",
        "tests/test_prototype.py::test_coupled_updates_rollback_aliases_and_defaults",
    ),
    "AC-013": _coverage(
        "tests/test_prototype.py::test_frozen_ancestors_and_copy",
        "tests/test_sol_phase03_blockers.py::test_sol014_non_string_bulk_names_precede_frozen_policy",
    ),
    "AC-014": _coverage(
        "tests/test_phase03_contract.py::test_scalar_bulk_failure_is_atomic_and_reset_updates_metadata",
        "tests/test_stateful.py::TestScalarTransactions",
        "tests/test_prototype.py::test_extras_destructive_metadata_and_errors",
    ),
    "AC-015": _coverage(
        "tests/test_prototype.py::test_nonidempotent_unchanged_normalizer_rejected_without_drift",
        "tests/test_inventory.py::test_sort_callback_failure_and_programming_error",
        "tests/test_sol_phase02_rereview.py::test_sol012_existing_model_public_validation_preserves_supplied_context",
    ),
    "AC-016": _coverage(
        "tests/test_transaction_remediation.py::test_every_prepared_swap_boundary_recovers",
        "tests/test_prototype.py::test_late_generator_and_reentrancy_recover",
        "tests/test_prototype.py::test_commit_slot_failure_restores_all_live_state",
    ),
    "AC-017": _coverage("tests/test_inventory.py::test_cached_computed_fields_are_invalidated"),
    "AC-018": _coverage(
        "tests/test_phase03_contract.py::test_scalar_copy_is_validated_and_independent",
        "tests/test_prototype.py::test_copy_ownership",
        "tests/test_inventory.py::test_validated_copy_rejects_unknown_keys_and_drift",
        "tests/test_prototype.py::test_frozen_ancestors_and_copy",
    ),
    "AC-019": _coverage(
        "tests/test_prototype.py::test_unsafe_inputs_hooks_and_trusted_paths_rejected"
    ),
    "AC-020": _coverage(
        "tests/test_compat_remediation.py::test_type_adapter_native_mode_keeps_dynamic_strict_and_extra_options",
        "tests/test_sol_phase03_rereview.py::test_sol017_json_entry_options_match_pinned_basemodel",
        "tests/test_sol_phase03_rereview_2.py::test_sol017_type_adapter_strict_json_matches_pinned_basemodel",
        "tests/test_sol_phase03_rereview_3.py::test_sol017_type_adapter_strict_strings_matches_pinned_basemodel",
        "tests/test_sol_phase03_rereview_3.py::test_sol017_type_adapter_json_preserves_field_specific_strictness",
        "tests/test_sol_phase03_rereview.py::test_sol017_rejected_strings_callback_cannot_mutate_entry_source",
        "tests/test_sol_phase02_rereview_2.py::test_sol013_failed_public_validation_does_not_mutate_existing_input",
        "tests/test_sol_phase02_rereview.py::test_sol012_existing_model_public_validation_preserves_supplied_context",
    ),
    "AC-021": _coverage(
        "tests/test_prototype.py::test_serializers_exclusions_computed_and_context"
    ),
    "AC-022": _coverage(
        "tests/test_phase03_evidence_contract.py::test_scalar_model_equality_and_hash_contract"
    ),
    "AC-023": _coverage(
        "tools/check_typing.py", "pyright --verifytypes pydandict --ignoreexternal"
    ),
    "AC-024": {
        **_coverage(
            "examples/library_config.py (direct/rebuilt clean-wheel execution)",
            "installed metadata, nested, HTTP and typing consumers",
            lanes=(_ARTIFACT_LANE,),
        ),
    },
    "AC-025": _coverage(
        "tests/test_sol_phase03_rereview.py::test_sol015_missing_provenance_cannot_replace_durable_evidence",
        "tools/qualify_package.py",
        lanes=(_ARTIFACT_LANE, _RUNTIME_LANE, _DOCS_LANE),
    ),
    "AC-026": {
        **_coverage(cast(str, _SCALAR_PROFILE["test"])),
        "stateful_profile": _SCALAR_PROFILE,
    },
    "AC-027": _coverage(
        "tests/test_stateful.py::TestTransactions",
        "tests/test_sol_phase02_rereview_5.py",
        "tests/test_sol_phase03_blockers.py",
    ),
    "AC-028": _coverage(
        "examples/library_config.py (direct/rebuilt clean-wheel execution)",
        "tools/check_docs.py",
        lanes=(_ARTIFACT_LANE, _DOCS_LANE),
    ),
}

# Behavioral applicability is separate from the OS/interpreter/job matrix.
# Cells below name exercised axes, observable rejection, and genuine exclusions;
# a unsupported operation is an applicable rejection test, not an omitted cell.
_BEHAVIOR_MATRIX = {
    "embedded-ingress": {
        "criteria": ["AC-002", "AC-020", "AC-027"],
        "tests": [
            "tests/test_sol_phase03_rereview_4.py::test_sol017_embedded_python_ingress_rejects_unsupported_sources",
        ],
        "axes": {
            "entry": ["ordinary BaseModel envelope", "TypeAdapter list"],
            "source": ["scalar subclass", "arbitrary attribute object"],
            "mode": ["python"],
        },
        "applicable": (
            "All cells reject unsupported original input before returning a model; "
            "standalone rejection and supported dictionary coercion are controls."
        ),
        "non_applicable": {
            "python-object/json-or-strings": (
                "JSON/StringsInput cannot carry arbitrary Python objects or scalar subclasses. "
                "Native embedding strictness is separately verified."
            ),
        },
    },
    "native-leaf-entry": {
        "criteria": ["AC-001", "AC-020"],
        "tests": ["tests/test_phase03_native_matrix.py::test_native_leaf_entry_matrix"],
        "axes": {
            "leaf": [
                "none",
                "bool",
                "int",
                "float",
                "str",
                "bytes",
                "decimal",
                "date",
                "datetime",
                "time",
                "timedelta",
                "uuid",
            ],
            "mode": ["python", "json", "strings"],
            "entry": ["class", "adapter"],
            "strict": [None, False, True],
        },
        "applicable": (
            "Every Cartesian cell except none/strings; native Python values and coercing "
            "Python strings compare accepted values/metadata or exact error "
            "locations/types to pinned BaseModel."
        ),
        "non_applicable": {
            "none/strings/*/*": (
                "StringsInput cannot represent null; Python/JSON null remain applicable and "
                "exercised."
            ),
            "parsed-custom-tzinfo/*": (
                "Custom tzinfo, including Pydantic TzInfo output, is outside the closed "
                "envelope. Naive native-mode temporal inputs and native datetime.timezone "
                "Python values are exercised."
            ),
        },
    },
    "annotation-entry": {
        "criteria": ["AC-001", "AC-002", "AC-020"],
        "tests": [
            "tests/test_phase03_native_matrix.py::test_annotation_entry_matrix",
            "tests/test_phase03_native_matrix.py::test_forward_generic_typed_extra_entry_matrix",
        ],
        "axes": {
            "annotation": [
                "nullable",
                "scalar union",
                "Literal",
                "Annotated",
                "Any",
                "object",
                "forward reference",
                "specialized generic",
                "typed scalar extra",
            ],
            "mode": ["python", "json", "strings"],
            "entry": ["class", "adapter"],
        },
        "applicable": (
            "All listed cells. Nullable strings exercises its non-null member; null is "
            "covered in the leaf matrix. Any/object exercise closed scalar output, not "
            "permission to escape mutable raw output."
        ),
        "non_applicable": {
            "unspecialized-generic/success": (
                "Explicit specialization is required; rejection is separately exercised."
            ),
            "concrete-mutable-annotation/success": (
                "Use supported ABC annotations; concrete annotation rejection is separately "
                "exercised."
            ),
        },
    },
    "native-options": {
        "criteria": ["AC-006", "AC-020"],
        "tests": [
            "tests/test_phase03_native_matrix.py::test_native_alias_extra_strict_option_matrix"
        ],
        "axes": {
            "mode": ["python", "json", "strings"],
            "entry": ["class", "adapter"],
            "extra_override": ["allow", "ignore", "forbid"],
            "strict": [None, False, True],
            "alias_flags": ["alias only", "name only"],
        },
        "applicable": (
            "All cells, including expected forbid rejection and field-specific strict "
            "date alongside coercing integer. Class allows extras; overrides cannot "
            "widen ongoing class policy."
        ),
        "non_applicable": {
            "from_attributes/json-or-strings": (
                "Those entry APIs do not expose from_attributes; Python's supported/rejected "
                "attribute ingress is covered separately."
            )
        },
    },
    "callback-isolation": {
        "criteria": ["AC-015", "AC-016", "AC-020"],
        "tests": [
            "tests/test_phase03_native_matrix.py::test_native_callback_source_isolation_and_context"
        ],
        "axes": {
            "mode": ["python", "json", "strings"],
            "entry": ["class", "adapter"],
            "callback": ["before", "wrap", "after"],
        },
        "applicable": (
            "All cells assert rejected callback cannot mutate caller raw graph, and "
            "receives original mode and supplied context. Existing protected model-input "
            "context/metadata/isolation controls remain anchors."
        ),
        "non_applicable": {
            "mutation/context-argument": (
                "Mapping mutators expose no context option; canonical transactions "
                "deliberately use Python mode and context=None."
            ),
            "exact-recursive-callback-count": (
                "Not guaranteed by the approved contract; SOL-011 is an existing nonblocking "
                "follow-up."
            ),
        },
    },
    "mapping-role-policy-freeze": {
        "criteria": [
            "AC-007",
            "AC-008",
            "AC-009",
            "AC-010",
            "AC-011",
            "AC-012",
            "AC-013",
            "AC-014",
        ],
        "tests": ["tests/test_phase03_policy_matrix.py::test_scalar_role_policy_freeze_matrix"],
        "axes": {
            "role": ["required", "defaulted", "nullable"],
            "extra_policy": ["allow", "ignore", "forbid"],
            "freeze": ["mutable", "model", "field"],
            "operation": [
                "setitem",
                "attribute",
                "update",
                "ior",
                "delete",
                "pop",
                "popitem",
                "clear",
                "reset",
                "existing setdefault",
                "empty update",
                "empty reset",
            ],
        },
        "applicable": (
            "All cells. Declared deletion/pop/clear, required reset and frozen writes "
            "are applicable rejection cells: values/order/fields-set/extra snapshots "
            "must be unchanged. No-op cells stay successful; update proves duplicate and "
            "keyword precedence; ior proves identity."
        ),
        "non_applicable": {
            "declared-field/removal-success": (
                "Declared fields are protected even nullable/defaulted; rejection cells are "
                "exercised, not silently skipped."
            )
        },
    },
    "mapping-extras-and-structure": {
        "criteria": ["AC-005", "AC-009", "AC-010", "AC-011", "AC-012", "AC-014"],
        "tests": [
            "tests/test_phase03_policy_matrix.py::test_scalar_extra_insertion_missing_and_removal_matrix",
            "tests/test_phase03_policy_matrix.py::test_scalar_empty_clear_validates_and_factory_reset_is_ordered",
            "tests/test_phase03_policy_matrix.py::test_scalar_malformed_batches_and_late_iterator_failure_are_atomic",
            "tests/test_phase03_evidence_contract.py::test_scalar_iterator_structure_and_exhaustion_contract",
        ],
        "axes": {
            "extra_policy": ["allow", "ignore", "forbid"],
            "model_frozen": [False, True],
            "structure": [
                "missing pop",
                "fallback",
                "extra insertion",
                "extra deletion",
                "extra popitem",
                "empty clear",
                "default factory field order/dedup",
                "malformed iterable",
                "late failure",
                "iterator before/after first next",
                "permanent exhaustion",
            ],
        },
        "applicable": (
            "Policy/freeze combinations are parameterized; standalone structural "
            "controls exercise meaningful transitions. Declared-key popitem/clear "
            "rejection is in the role matrix; scalar oracle retains typed extras and "
            "coupled fields."
        ),
        "non_applicable": {
            "forbid-or-ignore/persisted-extra-removal": (
                "Those policies cannot own extra keys; insertion rejection and missing "
                "removal are exercised instead."
            ),
            "frozen-model/successful-extra-structure-change": (
                "Frozen models cannot insert/remove; rejection and no-op cells remain applicable."
            ),
        },
    },
    "leaf-mapping-serialization-copy": {
        "criteria": ["AC-003", "AC-004", "AC-007", "AC-012", "AC-014", "AC-018", "AC-021"],
        "tests": [
            "tests/test_phase03_native_matrix.py::test_scalar_leaf_mapping_copy_serialization_matrix"
        ],
        "axes": {
            "leaf": [
                "none",
                "bool",
                "int",
                "float",
                "str",
                "bytes",
                "decimal",
                "date",
                "datetime",
                "time",
                "timedelta",
                "uuid",
            ],
            "operation": [
                "read/default enumeration",
                "update",
                "validated copy",
                "reset",
                "Python dump",
                "JSON dump",
                "alias schema",
            ],
        },
        "applicable": (
            "All cells use exact supported canonical leaves; schema properties and "
            "native serialization compare to BaseModel. Exclusion/computed/context "
            "serializers are independently retained anchors."
        ),
        "non_applicable": {
            "lossy-serialization-as-construction": (
                "Transactions/copies never round-trip JSON; native Python canonical values "
                "are required."
            )
        },
    },
    "equality-hashing": {
        "criteria": ["AC-022"],
        "tests": [
            "tests/test_phase03_evidence_contract.py::test_scalar_model_equality_and_hash_contract"
        ],
        "axes": {
            "model": ["mutable", "frozen"],
            "comparison": ["same model", "different extras", "dict"],
            "hash": ["mutable rejection", "frozen BaseModel parity"],
        },
        "applicable": (
            "Observable equality and mutable/frozen hash controls; stale nested equality "
            "is independently retained."
        ),
        "non_applicable": {
            "mutable-model/hash-success": (
                "Mutable DictModels are unhashable; TypeError is exercised."
            )
        },
    },
}

for _behavior in _BEHAVIOR_MATRIX.values():
    for _criterion in cast(list[str], _behavior["criteria"]):
        _entry = _AC_TEST_LANE_MAP[_criterion]
        _nodes = cast(list[str], _entry["tests"])
        _nodes.extend(node for node in cast(list[str], _behavior["tests"]) if node not in _nodes)

_AC_TEST_LANE_MAP["AC-001"]["tests"] = cast(list[str], _AC_TEST_LANE_MAP["AC-001"]["tests"]) + [
    "tests/test_phase03_native_matrix.py::test_native_timezone_python_envelope"
]
_AC_TEST_LANE_MAP["AC-002"]["tests"] = cast(list[str], _AC_TEST_LANE_MAP["AC-002"]["tests"]) + [
    "tests/test_phase02_contract.py::test_generic_models_must_be_explicitly_specialized",
    "tests/test_phase02_contract.py::test_custom_timezone_values_are_rejected_without_state_escape",
    "tests/test_phase02_contract.py::test_cycles_and_ordinary_base_models_are_rejected",
]


for _criterion, _proofs in {
    "AC-001": ["test_deferred_constructor_retains_caller_namespace"],
    "AC-016": ["test_native_default_factory_cannot_mutate_caller_field"],
    "AC-020": [
        "test_native_default_factory_cannot_mutate_caller_field",
        "test_python_attribute_ingress_retains_closed_source_boundary",
    ],
}.items():
    cast(list[str], _AC_TEST_LANE_MAP[_criterion]["tests"]).extend(
        "tests/test_phase03_native_matrix.py::" + _proof for _proof in _proofs
    )


for _criterion, _proofs in {
    "AC-003": ["test_scalar_mapping_consumers_do_not_invoke_serializers"],
    "AC-004": ["test_scalar_mapping_consumers_do_not_invoke_serializers"],
    "AC-011": ["test_scalar_fieldless_rejected_clear_and_typed_extra_reset_errors"],
    "AC-012": ["test_scalar_fieldless_rejected_clear_and_typed_extra_reset_errors"],
    "AC-014": ["test_scalar_cache_metadata_context_failure_and_noop_transitions"],
    "AC-015": ["test_scalar_cache_metadata_context_failure_and_noop_transitions"],
    "AC-017": ["test_scalar_cache_metadata_context_failure_and_noop_transitions"],
    "AC-018": ["test_scalar_copy_and_inherited_api_inventory"],
    "AC-019": ["test_scalar_copy_and_inherited_api_inventory"],
    "AC-021": ["test_scalar_cache_metadata_context_failure_and_noop_transitions"],
}.items():
    cast(list[str], _AC_TEST_LANE_MAP[_criterion]["tests"]).extend(
        "tests/test_phase03_evidence_contract.py::" + _proof for _proof in _proofs
    )


def qualifying_source(source_commit: str, relevant_status: str) -> bool:
    """Never attribute uncommitted implementation or verification to HEAD."""
    return bool(_COMMIT.fullmatch(source_commit)) and not relevant_status.strip()


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
            library_example = work / f"{label}-library_config.py"
            library_example.write_text((ROOT / "examples" / "library_config.py").read_text())
            dependency_records[f"{label}_library_example"] = execute(
                [str(bare_python), str(library_example)], work, env=clean_env
            ).stdout
            metadata_consumer = (
                "from importlib.metadata import distribution\n"
                "from pathlib import Path\n"
                "dist = distribution('pydandict')\n"
                "assert dist.metadata['Name'] == 'pydandict'\n"
                "assert dist.version == '0.2.0'\n"
                "assert dist.metadata['License-Expression'] == 'MIT'\n"
                "runtime = [item for item in (dist.requires or []) if 'extra ==' not in item]\n"
                "assert runtime == ['pydantic==2.13.4'], runtime\n"
                "licenses = [item for item in (dist.files or []) "
                "if str(item).lower().endswith('licenses/license')]\n"
                "assert len(licenses) == 1\n"
                "assert Path(dist.locate_file(licenses[0])).read_text().startswith('MIT License')\n"
                "print('metadata verified')\n"
            )
            dependency_records[f"{label}_metadata"] = execute(
                [str(bare_python), "-c", metadata_consumer], work, env=clean_env
            ).stdout
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
                "class Config(DictModel):\n"
                "    low: int = 1\n"
                "    high: int = 3\n"
                "cfg = Config()\n"
                "assert dict(cfg) == {'low': 1, 'high': 3} and cfg.model_fields_set == set()\n"
                "cfg.update(low=5, high=8)\n"
                "assert (cfg.low, cfg.high) == (5, 8)\n"
                "copy_cfg = cfg.model_copy(update={'low': 6})\n"
                "assert copy_cfg.low == 6 and cfg.low == 5\n"
                "cfg.reset('low', 'high')\n"
                "assert dict(cfg) == {'low': 1, 'high': 3}\n"
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
        source_commit = execute(["git", "rev-parse", "HEAD"], ROOT).stdout.strip()
        relevant_status = execute(
            [
                "git",
                "status",
                "--porcelain",
                "--",
                "src",
                "tests",
                "tools",
                "examples",
                "pyproject.toml",
                ".github",
                "LICENSE",
            ],
            ROOT,
        ).stdout
        hashes["resolved_dependencies"] = dependency_records
        hashes["commands"] = commands
        hashes["candidate_source_commit"] = source_commit
        hashes["relevant_worktree_status"] = relevant_status
        if not qualifying_source(source_commit, relevant_status):
            # Mocked or incomplete runs remain useful orchestration checks, but
            # must never replace durable release evidence or claim qualification.
            print(
                json.dumps(
                    {
                        "qualification_status": "non-qualifying",
                        "reason": (
                            "source identity was unavailable or relevant files differ from HEAD"
                        ),
                        "artifact_measurements": hashes,
                    },
                    sort_keys=True,
                )
            )
            return 0
        hashes["qualification_status"] = "qualified"
        hashes["source_commit"] = source_commit
        hashes["qualification_profile"] = "phase-0.3-scalar-installed-consumers"
        hashes["scalar_stateful_profile"] = _SCALAR_PROFILE
        hashes["ac_test_lane_map"] = _AC_TEST_LANE_MAP
        hashes["behavior_matrix"] = _BEHAVIOR_MATRIX
        hashes["execution_reconciliation"] = (
            "docs/research/phase-0.3-final-execution.json; compare its source identity "
            "and file hashes before reusing any execution. Presence is not a passing gate."
        )
        hashes["observed_failures"] = []
        hashes["limitations"] = [
            "This local package qualification does not prove every advertised CI lane.",
            "The full runtime suite, scalar stateful profile and docs checker are recorded as "
            "external required gates rather than asserted as executed here.",
        ]
        research = ROOT / "docs" / "research"
        research.mkdir(parents=True, exist_ok=True)
        (research / "phase-0.3-results.json").write_text(
            json.dumps(hashes, indent=2, sort_keys=True) + "\n"
        )
        (research / "phase-0.3-findings.md").write_text(
            "# Phase 0.3 qualification findings\n\n"
            f"Source commit: `{hashes['source_commit']}`\n\n"
            "This qualifying record was generated after direct and sdist-rebuilt wheel "
            "qualification. Both isolated bare environments executed the "
            "installed `examples/library_config.py` workflow with `PYTHONPATH` "
            "cleared. See `phase-0.3-results.json` for exact commands, resolved "
            "dependencies and SHA-256 artifact identities.\n\n"
            "## AC-to-test/lane evidence\n\n"
            + "\n".join(
                "- "
                f"{criterion}: nodes: {', '.join(cast(list[str], entry['tests']))}; "
                "lanes: "
                + "; ".join(
                    f"{lane['name']} ({lane['execution']})"
                    for lane in cast(list[dict[str, str]], entry["lanes"])
                )
                for criterion, entry in _AC_TEST_LANE_MAP.items()
            )
            + "\n\n## Matrix applicability\n\n"
            + "\n".join(
                f"- {criterion}: "
                + "; ".join(
                    f"{cell}: {details['status']} ({details['reason']})"
                    for cell, details in cast(
                        dict[str, dict[str, str]], entry["matrix_cells"]
                    ).items()
                )
                for criterion, entry in _AC_TEST_LANE_MAP.items()
            )
            + "\n\n"
            "AC-024's local artifact lane executes the direct and sdist-rebuilt scalar "
            "example and installed consumers; AC-025 records source, interpreter/platform, "
            "commands, resolutions and hashes. AC-026 records its deterministic stateful "
            "settings, while its execution remains an external runtime gate.\n\n"
            "`ac_test_lane_map`, `scalar_stateful_profile`, `observed_failures` and "
            "`limitations` distinguish actual local artifact execution from required external "
            "runtime/docs lanes. Non-qualifying runs with no valid Git source identity leave "
            "these durable records untouched. Relevant uncommitted source/test/tool changes "
            "also prevent replacement. See `phase-0.3-final-execution.json` for a "
            "bounded execution reconciliation, including failures and exact candidate scope; "
            "that record is not automatic qualification of a later candidate.\n"
        )
        for label, artifact in (("direct", wheel), ("rebuilt", rebuilt_wheel)):
            if not artifact.is_file():
                raise RuntimeError(f"{label} artifact disappeared during qualification")
        print(json.dumps(hashes, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
