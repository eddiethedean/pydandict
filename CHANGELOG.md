# Changelog

## Unreleased

## 0.3.0 - Unreleased

### Added

- Qualify the scalar mapping, mutation, default/reset, metadata, frozen and
  validated-copy contract, retaining the supported nested ownership envelope.
- Add scalar native-entry/policy matrices, deterministic stateful verification
  and the runnable `examples/library_config.py` workflow.
- Record independent review PASS for all 28 Phase 0.3 acceptance criteria and
  all previous release blockers, with source-qualified CI/artifact evidence.

### Fixed
- Reject non-string `pop` mutation keys before fallback handling, matching the
  documented mutation-key contract. Code using non-string keys with a `pop`
  fallback must now use a string key or a read-only `get` fallback.
- Preserve native JSON/strings validation and restore unsupported Python-input
  rejection when `DictModel` is embedded in ordinary models or TypeAdapter
  collections; retain validated canonical mutation/copy behavior.
- Reject unsupported original string subclasses and enums before native scalar
  coercion, including ordinary-model embedding. Preserve native validation state
  and public error locations through the pinned compatibility adapter.

### Release scope

- Python 3.11–3.14, exact `pydantic==2.13.4`, and MIT licensing remain unchanged.
- Native input auditing adapts Pydantic's private validator factories and native
  error layout. Requalify this integration before changing the pinned version;
  it adds no framework-plugin support guarantee.
- No arbitrary nested-type expansion, thread-safety, persistence or unchecked
  construction support is added. No persisted data migration is required.
- Version 0.3.0 is prepared but has not been tagged or published. Replace the
  Unreleased date only when publication is explicitly initiated.

## 0.2.0 - 2026-09-14

### Changed

- **Breaking:** declare mutable fields with `MutableSequence`, `MutableMapping`
  and `MutableSet` rather than concrete `list`, `dict` and `set` annotations,
  including nested/union occurrences and typed-extra values. Ordinary input and
  serialized container shapes remain unchanged. See the [migration contract](docs/phase-0.2-plan.md#annotation-and-owned-value-envelope).
- **Breaking:** explicitly specialize generic `DictModel` classes before
  constructing instances; unbound generic construction is rejected.

### Phase 0.2 implementation

- Enforce ABC mutable annotations, explicit generic specialization and fail-closed
  diagnostics for unsupported values and ownership boundaries.
- Add strict source and consumer typing checks, independent negative-fixture
  validation, a Pydantic compatibility adapter and clean wheel/sdist artifact
  qualification.
- Expand CI to the supported Python and operating-system matrix.
- Resolve the Sol release blockers: deferred/typed-extra annotations, safe hash
  positions, nested model identity writes, schema/cache isolation and rebuilds,
  generic private typing, exact typing evidence, both artifact consumers and
  guarded cache disposal.
- Acquire transaction guards before input callbacks, preserve supplied public
  validation context and detach existing-model inputs before user validation so
  failures cannot corrupt the source model.
- Measure baseline `07fec9b` and candidate production source across flat, linear
  and mixed workloads, with three runs, correctness checks, separate allocation
  measurements and root-validation counts; preserve Phase 0.1 evidence.

### Documentation

- Add the bounded Phase 0.2 architecture and implementation contract, with
  resolved target decisions, AC-001–028, verification matrix and implementation
  sequence.
- Record independent Sol review PASS for AC-001–028 and all release blockers.
- Enable GitHub private vulnerability reporting and document alpha support,
  maintainer triage and the advisory/release process.

### Fixed

- Match standard virtualenv platform defaults in artifact qualification so
  managed macOS interpreters retain access to their shared libraries.

## 0.1.0 - 2026-09-13

### Added

- Phase 0.1 integrated `pydandict` package (`0.1.0`), established as the
  project's starting baseline, with the original prototype retained as evidence.
- Atomic root transactions, private mutable protocol guards, stable/stale ownership,
  validated copies, canonical alias handling and Pydantic serialization/schema hooks.
- 87 runtime tests, stateful and injected-failure checks, installed typing tests,
  isolated library/FastAPI artifact consumers, strategy controls and initial benchmarks.
- Reproducible prototype evidence and a Phase 0.2 hardening/finalization plan.
- Reusable GitHub Actions checks and a tag-gated PyPI Trusted Publishing release
  workflow, with a package preflight that prevents unqualified publishing.

- Planning documentation for PydanDict and its primary `DictModel` base class.
- Proposed mapping API, transactional mutation contract, nested ownership design,
  Pyright strategy, Pydantic/FastAPI compatibility plan, and decision log.
- Interoperability and competition analysis, acceptance testing, security/performance
  considerations, roadmap, and contributing guidance.
- Documentation checks and reproducible upstream behavior/typing probes.
- Proposed quality bar, dependency-ordered W01–W13 implementation backlog,
  integrated feasibility gate, measurable qualification thresholds, and a concrete
  artifact/release checklist.
- Automated library/FastAPI consumer qualification and maintainer walkthroughs,
  with no external trials or additional participants required.
- Proposed detached removal-result semantics, ownership retention/recovery checks,
  and benchmark budget selection before beta.

### Fixed

- Include the root roadmap in documentation validation and correct the documentation
  index's security/performance link.

This first release is an alpha scoped to the documented Phase 0.1 support envelope.
Production API details marked as proposed and broader support gates remain subject
to Phase 0.2 qualification.
