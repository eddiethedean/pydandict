# Changelog

## Unreleased

### Documentation

- Add the bounded Phase 0.2 architecture and implementation contract, with
  resolved target decisions, AC-001–028, verification matrix and implementation
  sequence. This planning change does not implement or release Phase 0.2.

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
