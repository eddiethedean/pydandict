# Roadmap and release plan

The roadmap uses pre-1.0 release phases. Each `0.x` phase is a usable release
checkpoint with a deliberately narrow support boundary; phases are gated by
evidence, not elapsed time. The current repository is at `0.1` planning baseline.

## 0.1 — Planning baseline

- [x] Inspect the new repository and preserve established product decisions.
- [x] Document product, API, architecture, mutation, ownership, typing, compatibility,
  interoperability, competition, testing, security/performance, and contribution plans.
- [x] Record small reproducible upstream probes and unresolved feasibility gates.
- [ ] Review proposed contracts D07–D15 during the implementation kickoff.

Exit: linked, internally consistent planning set with no implementation claims.

## 0.2 — Feasibility prototype

| Work item | Output | Exit criterion |
| --- | --- | --- |
| G1 model/mapping bridge | Minimal implementation plus strict typing and FastAPI fixtures | BaseModel/ABCs recognized, key iteration and model serialization coexist |
| G2 atomic state changes | Candidate/commit experiments, validator compatibility report | Coupled updates and rollback; no drift of unchanged values; metadata preserved |
| G3 nested ownership | Guard experiments for list/dict/set/nested DictModel | Root constraints and escaped references protected; schema/type behavior acceptable |

Keep prototypes small and disposable. G1–G3 can be investigated independently,
then must be tested together. Review prototype findings before establishing the
production internals. If a core goal proves infeasible, revise the design openly;
do not substitute a weaker guarantee under unchanged documentation.

## 0.3 — Minimal package and scalar core

Create `src/pydandict`, build metadata, development dependencies, `py.typed`, CI,
and tests. Implement reads, class namespace policy, scalar field/extra writes,
bulk changes, errors, defaults/reset, metadata, frozen handling, and safe copies.
Resolve trusted/deprecated APIs. Choose the license and Python/Pydantic floor.

Exit: T1–T6/T10 pass for the explicitly supported scalar subset; unsupported
mutable values fail clearly. The `0.3` release must advertise that subset and
must not claim full lifetime support for arbitrary nested data.

## 0.4 — Ownership and ecosystem integration

Integrate the G3 ownership design for its proven supported value envelope. Close
all ordinary mutation paths, aliasing, stale handles, parent constraints, and
copy behavior. Exercise serializers, schemas, unions, generics, and FastAPI on
the selected dependency matrix. Finish migration and error examples.

Exit: T7–T9 pass, G1–G4 resolved for the proposed `0.4` release, and the supported-type
table matches actual behavior. No unguarded mutable fallback exists.

## 0.5 — Beta hardening

Run stateful/adversarial tests, measure performance and memory, review inherited
bypass paths, and test installed artifacts. Have independent application/library
consumers try the mapping and framework use cases. Resolve all data-corruption,
typing-contract, and serialization-leak defects before release candidates.

Exit: T1–T12 pass; examples run; support bounds and limitations are published;
API signatures, error codes, and deliberate BaseModel divergences are stable.

## 0.6 — Release candidate

Review the exact candidate commit, build and test wheel/sdist, verify metadata and
license, confirm package-name ownership, prepare release notes, and validate the
candidate through the configured secure release process. Install from the
distribution and run a consumer smoke check. A docs push is not a package release;
this planning task does not publish to PyPI or create a release tag.

The `0.6` release candidate requires the lifetime guarantee for the advertised
support envelope, real BaseModel/Mapping identity, atomic mutation, strict typing
evidence, and working Pydantic/FastAPI integration. Outstanding core gates block
the `1.0` stable release.

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
release matrix and the advertised lifetime guarantee has survived real consumer
testing. After that, follow the stable support policy above.

Consider optional literal-key typing tools, conversion from existing models,
additional safely owned types, and measured optimizations only when users show a
need. Public typed collection families, persistence, and reactivity remain outside
the package's core mission unless explicitly reconsidered through design review.
