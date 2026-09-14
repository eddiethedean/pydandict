# Quality bar for a dependable dependency

This is a proposed acceptance policy for implementation and release, not a report
of achieved results. Pydandict should earn trust through a small, understandable
contract, strong failure behavior, useful tooling, and runnable consumer projects.
Adding public features is secondary to making the core dependable. The
[Phase 0.1 results](research/prototype-findings.md) establish our starting evidence;
this document remains the higher bar for a supported production release.

## What top tier means here

| Dimension | Required outcome by 1.0 | Evidence and release blocker |
| --- | --- | --- |
| Correctness | Every advertised public mutation preserves I1–I8 | All applicable T3–T7 cases pass; any reproducible invalid state, partial commit, or ownership escape blocks release |
| Usability | Canonical keys, atomic update, nested references, and errors are clearly demonstrated | Three executable user journeys and isolated consumer projects below; unresolved core workflow failures block 1.0 |
| Typing | Precise attributes and honest mapping types without consumer casts | Strict installed-package fixtures plus 100% public completeness from Pyright; the documented iterator override remains an explicit divergence |
| Integration | Ordinary Pydantic and FastAPI paths work within published bounds | T8 differential and HTTP tests on the release matrix; unexplained schema or payload differences block release |
| Performance | Costs are predictable and fit representative uses | Versioned timing/memory report and numeric budgets selected from measured workloads before beta; breached budgets block qualification until resolved or explicitly revised |
| Distribution | Users install exactly the artifacts that were tested | Wheel and sdist rebuild/install checks, metadata/license review, and artifact hashes in the release record |
| Maintainability | Compatibility-sensitive code and contract changes are reviewable | Adapter inventory, decision records, focused regression tests, and documented support/triage ownership |

The complete measurement protocol is in [testing](testing.md), the workload design
in [security and performance](security-performance.md), and release operations in
the [roadmap checklist](../ROADMAP.md#release-checklist).

## Three reference user journeys

Implementation will introduce an `examples/` directory. These filenames are planned
deliverables, not runnable files in the current repository. Each example must run
against an installed wheel, contain assertions, and have a corresponding guide.

| Planned example | User task | Acceptance |
| --- | --- | --- |
| `examples/library_config.py` | Replace an internal settings dictionary with a constrained record | Mapping-only reader and writer use the same object; coupled update succeeds; rejected update preserves values and fields-set; reset restores validated defaults |
| `examples/fastapi_records.py` | Accept, change, and return one API record | Standard request and response annotations, invalid request response, alias/exclusion behavior, and OpenAPI checks; no custom encoder or framework adapter |
| `examples/nested_budget.py` | Safely edit a nested configuration through saved references | List edit and child edit enforce root budget; rejected edits roll back; input aliases are detached; replaced handles fail clearly; copies are independent |

Use small domain examples without field names that collide with mapping methods.
Include one actionable failure and its recovery in each guide. At beta, maintain
two isolated consumer projects: a small mapping-oriented library and a FastAPI
application. Install the built wheel into each project's clean environment, outside
the source checkout. Exercise their public workflows without importing package
internals. Record environment, attempted task, required workarounds, outcome, and
remaining issues. These checks run automatically; the maintainer can also follow
the guides from a clean environment. No external participants, recruitment, or
third-party trials are required for any milestone. This is reproducible integration
and documentation evidence, not a claim of independently measured user adoption.

## Documentation as part of the API

By beta, documentation must include:

- A quickstart covering install, field declaration, reads, one successful update,
  and one rejected update with unchanged state.
- A decision guide: choose DictModel for mutable schema-defined mappings; choose
  a simpler boundary-validation approach when lifetime validation is unnecessary.
- A migration guide covering namespace collisions, pair-to-key iteration,
  deletion/reset, aliases, copy/construct, metadata snapshots, and nested types.
- An explicit supported-values and validator table with working examples,
  detectable rejection behavior, and limitations that require author discipline.
- API reference signatures, mutator return values, exception classes, stable
  Pydandict error codes, and nested error-location examples. Do not promise stable
  upstream message text or expose raw sensitive input in troubleshooting examples.
- A performance page with reproducible workloads and a support page with exact
  tested versions, platform coverage, and deliberate BaseModel differences.

Released examples execute in CI; planning examples remain clearly labeled until
then. Publish docs corresponding to each released version and distinguish unreleased
documentation. A polished README cannot substitute for passing acceptance tests.

## Evidence records

Create an evidence record for each closed gate and release candidate under
`docs/research/` when results exist. Use this structure:

| Field | Required content |
| --- | --- |
| Identity | Gate or release, commit, date, responsible maintainer and recorded review outcome |
| Environment | Python, OS/architecture, exact resolved dependencies, commands |
| Scope | Supported types, validator/hook contract, applicable T groups and I invariants |
| Results | Passing and failing cases, diagnostic output, benchmark artifacts, CI run links |
| Limits | Excluded combinations, detection behavior, private upstream APIs used |
| Decision | Pass, fail, or deferred; rationale; follow-up issue and dependent milestone |

An open gate has no invented passing result. A failing core guarantee cannot be
waived by an expected failure marker, a performance improvement, or a README
qualification added only after the release. A reduced support envelope needs a
decision record, updated examples/tests, and a fresh qualification run.

## Maintenance after launch

Assign a release and security triage owner before distribution. Classify reported
bugs by impact: invalid state/partial mutation/serialization disclosure first,
advertised API or integration failures second, ergonomics and optimizations after
those. Publish a minimal reproduction template and retain regressions in tests.
Response-time commitments need an actual maintainer commitment; none is assumed.

Proposed initial maintenance scope is the latest stable minor, with older series
explicitly listed as supported or unsupported. Do not promise LTS at launch.
Test upstream updates before expanding dependency bounds, and publish migration
notes for every changed public behavior. Scope growth requires a demonstrated
consumer need and maintenance cost, preserving the [product boundary](product.md).
