# Phase 0.3 qualification findings

Source commit: `b8ff5071d215baca6c44a109ba6d0ebbae627ded`

This qualifying record was generated after direct and sdist-rebuilt wheel qualification. Both isolated bare environments executed the installed `examples/library_config.py` workflow with `PYTHONPATH` cleared. See `phase-0.3-results.json` for exact commands, resolved dependencies and SHA-256 artifact identities.

## Evidence map and limitations

- AC-024: direct/rebuilt installed scalar example, consumer and installed metadata-policy records.
- AC-025: source commit, interpreter/platform, commands, dependency resolutions and direct/rebuilt artifact hashes.
- AC-026: settings/replay profile is recorded, but its execution belongs to the repository runtime/CI gate.
- AC-028: installed scalar library-config example records; docs checking belongs to its separate gate.

`ac_test_lane_map`, `scalar_stateful_profile`, `observed_failures` and `limitations` make the boundary between this local artifact run and required full CI evidence explicit. Non-qualifying runs with no valid Git source identity leave these durable records untouched.
