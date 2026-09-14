# Phase 0.3 qualification findings

Source commit: `912b309350d94f75b8a8608f71c83b8d13132e05`

This qualifying record was generated after direct and sdist-rebuilt wheel qualification. Both isolated bare environments executed the installed `examples/library_config.py` workflow with `PYTHONPATH` cleared. See `phase-0.3-results.json` for exact commands, resolved dependencies and SHA-256 artifact identities.

## AC-to-test/lane evidence

- AC-001: nodes: tests/test_sol_phase03_blockers.py::test_sol017_strict_scalar_entry_modes_match_pinned_basemodel, tests/test_sol_phase03_rereview_2.py::test_sol017_type_adapter_strict_json_matches_pinned_basemodel; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-002: nodes: tests/test_phase02_contract.py::test_concrete_mutable_annotations_fail_with_migration_hint, tests/test_hash_ingress.py::test_unhashable_model_members_get_the_ownership_diagnostic; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-003: nodes: tests/test_phase03_contract.py::test_scalar_reads_views_and_canonical_namespace; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-004: nodes: tests/test_phase03_contract.py::test_scalar_reads_views_and_canonical_namespace; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-005: nodes: tests/test_prototype.py::test_identity_serialization_and_mapping_views; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-006: nodes: tests/test_inventory.py::test_explicit_public_alias_flags; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-007: nodes: tests/test_phase03_contract.py::test_scalar_bulk_failure_is_atomic_and_reset_updates_metadata; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-008: nodes: tests/test_stateful.py::TestScalarTransactions; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-009: nodes: tests/test_phase03_contract.py::test_non_string_pop_is_rejected_before_fallback, tests/test_sol_phase03_blockers.py::test_sol014_non_string_bulk_names_precede_frozen_policy; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-010: nodes: tests/test_stateful.py::TestScalarTransactions; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-011: nodes: tests/test_prototype.py::test_extras_destructive_metadata_and_errors; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-012: nodes: tests/test_stateful.py::TestScalarTransactions; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-013: nodes: tests/test_prototype.py::test_frozen_ancestors_and_copy; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-014: nodes: tests/test_phase03_contract.py::test_scalar_bulk_failure_is_atomic_and_reset_updates_metadata, tests/test_stateful.py::TestScalarTransactions; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-015: nodes: tests/test_prototype.py::test_nonidempotent_unchanged_normalizer_rejected_without_drift; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-016: nodes: tests/test_transaction_remediation.py::test_every_prepared_swap_boundary_recovers; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-017: nodes: tests/test_inventory.py::test_cached_computed_fields_are_invalidated; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-018: nodes: tests/test_phase03_contract.py::test_scalar_copy_is_validated_and_independent; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-019: nodes: tests/test_prototype.py::test_unsafe_inputs_hooks_and_trusted_paths_rejected; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-020: nodes: tests/test_compat_remediation.py::test_type_adapter_native_mode_keeps_dynamic_strict_and_extra_options, tests/test_sol_phase03_rereview.py::test_sol017_json_entry_options_match_pinned_basemodel, tests/test_sol_phase03_rereview_2.py::test_sol017_type_adapter_strict_json_matches_pinned_basemodel; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-021: nodes: tests/test_prototype.py::test_serializers_exclusions_computed_and_context; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-022: nodes: tests/test_inventory.py::test_stale_child_repr_equality_and_metadata; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-023: nodes: tools/check_typing.py, pyright --verifytypes pydandict --ignoreexternal; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-024: nodes: examples/library_config.py (direct/rebuilt clean-wheel execution), installed metadata, nested, HTTP and typing consumers; lanes: local package qualification (executed by this driver for the recorded source/artifacts)
- AC-025: nodes: tests/test_sol_phase03_rereview.py::test_sol015_missing_provenance_cannot_replace_durable_evidence, tools/qualify_package.py; lanes: local package qualification (executed by this driver for the recorded source/artifacts); CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-026: nodes: tests/test_stateful.py::TestScalarTransactions; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-027: nodes: tests/test_stateful.py::TestTransactions, tests/test_sol_phase02_rereview_5.py, tests/test_sol_phase03_blockers.py; lanes: CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)
- AC-028: nodes: examples/library_config.py (direct/rebuilt clean-wheel execution), tools/check_docs.py; lanes: local package qualification (executed by this driver for the recorded source/artifacts); CI compatibility matrix (required external runtime gate; recorded separately from this artifact driver)

AC-024's local artifact lane executes the direct and sdist-rebuilt scalar example and installed consumers; AC-025 records source, interpreter/platform, commands, resolutions and hashes. AC-026 records its deterministic stateful settings, while its execution remains an external runtime gate.

`ac_test_lane_map`, `scalar_stateful_profile`, `observed_failures` and `limitations` distinguish actual local artifact execution from required external runtime/docs lanes. Non-qualifying runs with no valid Git source identity leave these durable records untouched.
