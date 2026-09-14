# Roadmap and release plan

PydanDict should become a dependable, focused dependency: one schema-defined object
with real model/mapping identity, atomic validated mutation, protected nested state,
honest types, and predictable costs. **Phase `0.1` is the working integrated
implementation and our starting baseline.** Its demonstrated behavior and explicit
limitations are recorded in the [prototype findings](docs/research/prototype-findings.md).

Phases are gated by evidence, not dates. The package was published as release
`0.1.0` from the matching tag after passing its workflow gates. Phase `0.2` hardens that baseline,
and broader package checkpoints begin at `0.3`, subject to license, compatibility
and artifact gates. Preserve and extend the Phase 0.1 tests and mechanisms during
hardening; do not restart from scratch.

The [quality bar](docs/quality-bar.md) defines measurable outcomes, and the
[implementation backlog](docs/implementation-plan.md) defines W01–W13 with
dependencies and acceptance criteria. Existing R1–R10, I1–I8, T1–T12 and G1–G5
remain the requirement, invariant, test and feasibility references.

## Priorities and critical path

1. Harden the integrated bridge, transaction and ownership baseline, and finalize
   its explicit support contracts before broadening the supported envelope.
2. Ship a small, correct scalar core, then qualify the complete supported nested
   envelope through the same engine and ecosystem paths.
3. Establish measured performance budgets, run automated consumer projects, and
   rehearse artifact releases before declaring stability.

Critical path: Phase 0.1 baseline W01–W05 → Phase 0.2 hardening → scalar
hardening W06–W07 → ownership/integration W08–W09 → release qualification
W10–W11 → candidate W12.
Optimization and extra APIs stay behind this path. No milestone requires external
participants or trials; all consumer qualification can run locally and in CI.

## 0.1 — Integrated implementation baseline

This is the project's implemented starting point, requested as Phase 0.1. Run the
package test suite and inspect the original [prototype guide](prototypes/README.md)
and [source/artifact evidence](docs/research/prototype-results.json).

- [x] Preserve the product requirements and linked design specifications.
- [x] Implement genuine BaseModel/mapping identity and the complete mapping surface.
- [x] Demonstrate isolated whole-model validation, atomic coupled changes, rollback,
  metadata/default handling and validated independent copies.
- [x] Implement finite-tree ownership with private mutable ABC guards, stable and
  stale handles, detached removal results, ancestor constraints and freeze checks.
- [x] Integrate aliases, recursive schemas, unions/generics, serializers and FastAPI.
- [x] Pass 87 runtime tests, including stateful sequences and injected commit failures,
  on Python 3.11.14 and 3.14.3.
- [x] Verify positive/negative installed typing, 100% public type completeness, and
  isolated library/HTTP consumers using direct and sdist-rebuilt wheels.
- [x] Record initial costs, retention checks, rejected approaches and remaining limits.
- [x] Promote the tested implementation into `src/pydandict`, add package metadata,
  production imports, and a root test suite covering the same contract.

Baseline boundary: package `pydandict` at release version `0.1.0`,
protocol-based mutable values, rerunnable canonical validators and one pinned
upstream stack. This is an implemented alpha baseline with a public release limited
to the documented support envelope. The release workflow publishes only artifacts
built from the matching `v0.1.0` tag.

## 0.2 — Prototype hardening and contract finalization

The [Phase 0.2 architecture and implementation contract](docs/phase-0.2-plan.md)
defines the bounded change, resolved target decisions, AC-001–028, verification
matrix and dependency-aware implementation sequence. The
[independent review](docs/reviews/phase-0.2-rereview-6.md) verified AC-001–028.
Version 0.2.0 was published through the existing release workflow on 2026-09-14.

Build directly on the Phase 0.1 package. Review and resolve the following before
broader support and release qualification; keep existing behavior covered.

- [x] Finalize mutable ABC annotations, concrete-container limitations, identity
  assignment/writeback semantics and container iterator policy (D20).
- [x] Finalize the validator/hook support table and rejection diagnostics. Preserve
  the no-drift and no-unguarded-fallback requirements.
- [x] Audit and isolate the canonical-schema, schema-reference, snapshot and commit
  mechanisms; add upstream boundary tests for the version-sensitive adapter (D21).
- [x] Expand adversarial/stateful coverage and measure larger/deeper graphs before
  choosing safe reductions in cloning or reconciliation overhead.
- [x] Review proposed contracts D07–D17/D19 with the prototype evidence; preserve
  the established no-external-trials constraint D18 and baseline decision D22.
- [x] Select the initial support floor and MIT license/metadata for the W05 scaffold;
  broader support remains a hardening decision.

Exit: reviewed production contracts, an adapter compatibility report, a passing
package regression suite and a concrete hardening plan. G1–G3 have
prototype evidence; their production qualification remains required. If a core
contract fails, record the case and revise the design openly before promotion.

## 0.3 — Minimal scalar core

The [Phase 0.3 architecture and implementation contract](docs/phase-0.3-plan.md)
defines the scalar qualification boundary, AC-001–028 and W05–W07 verification.
The [independent review](docs/reviews/phase-0.3-rereview-5.md) verifies all 28 ACs
and all previous blockers. Version 0.3.0 is in
[release preparation](docs/release.md#030-release-preparation), not yet published.
Build on Phase 0.2 and preserve its shipped nested behavior; this milestone does
not introduce a scalar-only runtime mode or remove existing ownership support.

Harden the root `src/pydandict` package and its build metadata. Carry forward the
relevant prototype tests while finalizing reads, class namespace policy, scalar field/extra writes,
bulk changes, errors, defaults/reset, metadata, frozen handling, and safe copies.
Qualify trusted/deprecated APIs and retain the selected MIT license and exact
Python/Pydantic policy for the next checkpoint. Keep FastAPI and quality tooling in
development/integration dependencies; retain Pydantic as the sole direct runtime
dependency.

Exit: T1–T6/T10 pass for the explicitly qualified scalar subset; mutable values
outside the existing closed envelope fail clearly. The `0.3` release must advertise
that subset and must not claim full lifetime support for arbitrary nested data. G1/G2 must pass
for this subset, G4 must cover its advertised matrix, and G5 must be resolved.

## 0.4 — Ownership and ecosystem integration

Integrate the G3 ownership design for its proven supported value envelope. Close
all ordinary mutation paths, aliasing, stale handles, parent constraints, and
copy behavior, including useful return values from removal operations. Exercise
serializers, schemas, unions, generics, and FastAPI on the selected dependency
matrix. Finish migration and error examples. Measure representative workloads
and select numeric timing/memory budgets before beta; record their rationale.

Exit: T7–T9 pass, G1–G4 resolved for the proposed `0.4` release, and the supported-type
table matches actual behavior. No unguarded mutable fallback exists.

## 0.5 — Beta hardening

Run stateful/adversarial tests, measure performance and memory, review inherited
bypass paths, and test installed artifacts. Run isolated library and FastAPI
consumer projects against the wheel, plus all three documented user journeys.
These are automated checks and maintainer-run walkthroughs; no external people
or trials are required. Resolve all data-corruption,
typing-contract, and serialization-leak defects before release candidates.

Exit: T1–T12 pass; examples run; support bounds and limitations are published;
API signatures, error codes, and deliberate BaseModel divergences are stable.
Meet the [qualification thresholds](docs/testing.md#qualification-thresholds),
including fault recovery, public typing completeness and ownership retention tests.

## 0.6 — Release candidate

Review the exact candidate commit, build and test wheel/sdist, verify metadata and
license, confirm package-name ownership, prepare release notes, and validate the
candidate through the configured secure release process. Install from the
distribution and run a consumer smoke check. A docs push is not a package release;
this prototype work does not publish to PyPI or create a release tag.

The `0.6` release candidate requires the lifetime guarantee for the advertised
support envelope, real BaseModel/Mapping identity, atomic mutation, strict typing
evidence, and working Pydantic/FastAPI integration. Outstanding core gates block
the `1.0` stable release.

## Release checklist

The latest completed checkpoint is PydanDict 0.2.0, published on 2026-09-14
through the tag-gated Trusted Publishing workflow. See the [0.2.0 release record](docs/release.md#020-release-record)
and [qualification evidence](docs/research/release-0.2.0-results.json).

Phase 0.3 has since passed [independent review](docs/reviews/phase-0.3-rereview-5.md).
The 0.3.0 candidate is prepared but unpublished; its version-specific checklist
is in [release preparation](docs/release.md#030-release-preparation).

Complete this checklist for every distributed checkpoint, scoped to its declared
support envelope. For `1.0`, the nested lifetime contract and the complete quality
bar are mandatory. Unchecked boxes here are future tasks, not passing results.

- [ ] Record the candidate commit, public API/support envelope, exact matrix,
  resolved G gates, known limitations and test/benchmark evidence.
- [ ] Pass applicable T1–T12 with no skipped or expected-failure case concealing
  a required behavior. Fix correctness/serialization failures before proceeding.
- [ ] Run strict consumer typing and public completeness against the installed
  package. Execute quickstart, migration and reference workflows from the artifacts.
- [ ] Build wheel and sdist from the candidate; inspect contents and metadata;
  build a wheel from the sdist in isolation and smoke-test both wheel paths outside
  the checkout. Check `py.typed`, license, declared bounds and absence of local files.
- [ ] Verify package-name ownership and the selected license; configure a private
  security reporting route and name the release/triage owner before distribution.
- [ ] Prepare versioned docs, changelog, migration notes and stable error-code
  reference. Label intended differences and unsupported cases prominently.
- [ ] Rehearse publication in the configured test environment, then publish only
  through an explicitly initiated release workflow. Use PyPI Trusted Publishing,
  restricted workflow permissions, and an environment limited to release jobs.
- [ ] Record hashes of the tested artifacts and upload those same artifacts.
  Validate installed import/version, typing marker and a consumer smoke check from
  the published distribution. Record the result and corrective action if it fails.

PyPI documents short-lived identity-based publishing in its
[Trusted Publishing guide](https://docs.pypi.org/trusted-publishers/). The
Trusted Publisher is configured for this repository. A sole
maintainer can perform the full release process; no separate human reviewer is a
release prerequisite. The original prototype task did not publish artifacts or
create release tags; the completed 0.2.0 release followed this process through
the tag-gated workflow.

## Version and support policy

Adopt semantic versioning from the first `0.x` release. Before 1.0, document
breaking changes prominently and treat each `0.x` release as potentially breaking.
After 1.0, changes to key
space, accepted mutation behavior, return types, alias interpretation, ownership,
or guaranteed errors are compatibility changes requiring appropriate versioning.

Security or correctness patches can reject previously accepted invalid state;
explain such changes and migration impact. Deprecate supported public APIs before
removal when practical. Internal modules remain private, but dependency upgrades
still require compatibility tests. A new Pydantic minor is supported only after
the matrix passes, not automatically because it satisfies a broad dependency spec.

Maintain a changelog, exact tested versions, known limitations, and migration notes
for every release. If a bad release is published, stop further publication, assess
yanking the affected distribution, and publish a corrective version; never silently
replace an existing artifact or rewrite a published tag.

## 1.0 and after

Publish `1.0` only after the `0.6` release candidate has passed the complete
release matrix and the advertised lifetime guarantee passes the stateful,
fault-injection and isolated consumer suites. Record a maintainer review of the
evidence; no external trial or independent participant is required. After that,
follow the stable support policy above and the [maintenance scope](docs/quality-bar.md#maintenance-after-launch).

Consider optional literal-key typing tools, conversion from existing models,
additional safely owned types, and measured optimizations only when users show a
need. Public typed collection families, persistence, and reactivity remain outside
the package's core mission unless explicitly reconsidered through design review.
