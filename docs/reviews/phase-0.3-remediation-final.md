# Phase 0.3 — Final blocker remediation

Candidate: `7476decadc479488c9ed14772e3b7719455817ae`. Production changes are in `d0e80850be769be2c85e7b1d1230b76cbeefcdc4`; the final candidate adds direct inventory proof without changing production.
Status: both blockers FIXED. [Exact-candidate CI](https://github.com/eddiethedean/pydandict/actions/runs/34893263306): all 11 applicable jobs passed.

## SOL-017 — Native TypeAdapter entry semantics

Status: FIXED. Related AC: AC-001/020.

Root cause: a root Python wrap handler erased native JSON/strings input semantics, and exception-whitelist replay imposed unconditional strictness instead of the original schema's options.

Production changes: [compatibility adapter](../../src/pydandict/_compat.py) keeps native JSON/strings validation until existing user callbacks or validated-field boundaries. Public Python input is cloned in a Python-only branch. Embedded schemas retain model shape for discriminator inference. The isolated constructor/public-Python/canonical wrappers are reconstructed from normalized schema nodes, preserving definitions, defaults, alias variants and class-local rebuild invalidation. The [core](../../src/pydandict/_core.py) installs ownership after native validation and retains the existing whole-root Python transaction engine. No error replay, global strictness, framework monkeypatch or dependency change remains.

Before verification: both independent third-review TypeAdapter regressions fail on the previous candidate; prior strict JSON rejection, extra overrides and callback isolation controls already pass.
After verification: both protected regressions, prior entry controls, scalar leaf/annotation/alias/extra/strict differentials, native callback/factory source isolation, deferred constructors, nested discriminators/recursive defaults and all 562 tests pass locally.

Related verification: [protected regressions](../../tests/test_sol_phase03_rereview_3.py), [native matrix](../../tests/test_phase03_native_matrix.py), existing compatibility and Phase 0.2 remediation tests. Protected third-review test SHA-256: `a0bab3487285dc2b91a0d171c6f1064f69f9e1b82275beb587c9598ed0749bd0`, unchanged.
Additional implementation verification: 346 native-matrix cases, 35 role/policy/freeze cases, nine direct evidence/consumer/cache/copy cases. These do not replace or alter protected tests.
Resolution criterion: pinned acceptance/rejection, native mode, options/context, isolation, ongoing extra policy and retained nested ownership must all remain green.

## SOL-015 — Complete auditable qualification inventory

Status: FIXED. Related AC: AC-025/028; approved P1/P5/P6.

Root cause: generic job labels and incomplete behavioral anchors did not demonstrate complete AC coverage or identify actual executed candidate lanes.

Changes: [qualification driver](../../tools/qualify_package.py) names real proof nodes for all 28 ACs, distinguishes eight runtime/two artifact/one docs cells, adds behavioral applicability and explicit exclusions, and rejects missing/dirty relevant-source identity without replacing durable evidence. New direct assertions close iterator exhaustion/invalidation, equality/hash, required/default/nullable/freeze, malformed batch, cache failure/no-op, fieldless clear, inherited copy/parse and mapping-consumer anchor gaps.

Before verification: third review confirms incomplete AC-005/022 anchors, missing behavioral non-applicability, and no executed-lane reconciliation.
After verification: all anchors resolve to actual collected nodes; local tests, static/docs gates and both fresh clean-wheel paths pass. All 11 exact-candidate CI jobs passed; each applicable AC cell links its actual job, patch interpreter, commands and proof nodes in the [final execution reconciliation](../research/phase-0.3-final-execution.json).
Related verification: [evidence controls](../../tests/test_phase03_evidence_contract.py), [policy matrix](../../tests/test_phase03_policy_matrix.py), protected non-qualifying provenance test, [fresh artifact record](../research/phase-0.3-results.json).
Additional verification: inline source-qualified checks exercise self update/in-place union, empty mapping consumers and exact missing-fallback identity.
Resolution criterion: every applicable cell must link actual candidate execution, commands, resolved versions, node inventory and artifact identity; non-applicable cells require reasons. Historical evidence and invalid-run preservation must remain intact.

## Behavioral applicability

The artifact record carries the full AC/node inventory and Cartesian axes. A rejection is an exercised cell, not a silent omission.

| Dimension | Exercised behavior | Explicit exclusion / non-applicability |
| --- | --- | --- |
| Scalar leaves × Python/JSON/strings × class/TypeAdapter × strict default/false/true | 12 exact leaves; accepted values/fields-set or error locations/types compared with pinned BaseModel | None cannot be represented by StringsInput; Python/JSON null remain exercised. Parsed custom tzinfo is outside the closed envelope; naive temporal native inputs and native datetime.timezone Python values are exercised. |
| Nullable/union/Literal/Annotated/Any/object/forward/generic/typed extras × modes/entries | Closed scalar annotation output; nullable non-null strings branch; explicit generic specialization | Unspecialized generic and concrete mutable annotations have rejection controls, not success claims. |
| Native options × modes/entries | Alias-only/name-only; extra allow/ignore/forbid; call strictness alongside field-specific strictness; context/isolation | JSON/strings APIs do not expose from_attributes. Arbitrary-object attribute ingress remains deliberately rejected. |
| Before/wrap/after callbacks and default factories × modes/entries | Caller graph unchanged after callback/factory failure; native mode/context retained | Mutators expose no construction-context argument; canonical mutation/copy are Python/context=None. Exact recursive callback count is not promised. |
| Required/defaulted/nullable × allow/ignore/forbid × model/field/unfrozen × mutators | Frozen/equal/mixed-write rejection, declared-removal rejection, reset metadata, duplicate/keyword precedence, union identity, existing/missing/empty no-ops | Successful declared deletion, frozen structural changes, and persisted extras under ignore/forbid cannot occur; meaningful rejection/missing cells are exercised. |
| Mapping/copy/serialization/hash | Every leaf in default read/update/reset/copy/dump/JSON/schema; direct consumer/cache/inherited API assertions; frozen hash parity | Copies/transactions never construct through lossy JSON; mutable hash success is excluded and rejection exercised. |
| CI jobs | Eight runtime, two clean-artifact, one documentation jobs | Release-only package preflight is skipped on normal push by unchanged workflow design; no publication is attempted. |

## Required gates

- Full runtime suite: 562 passed in 114.18s; both deterministic stateful machines retain max_examples=100, stateful_step_count=100, deadline=None, derandomize=True.
- Lint and formatting: passed; 32 required files formatted.
- Strict positive/negative typing: passed; installed public completeness 100%.
- Documentation: 50 Markdown files, 274 local links, eight Python examples, zero errors before this final report.
- Fresh direct and sdist-rebuilt wheels: passed in clean external bare/runtime/typing environments, with PYTHONPATH cleared and import paths outside the checkout; actual scalar example, nested/HTTP consumers, name/version/MIT/dependency/py.typed metadata and exact negative diagnostics verified.
- CI: all eight runtime, two artifact and one docs jobs passed for the exact final candidate; every runtime job reports 562 passed and 100% public completeness. Both artifact jobs record qualified direct/rebuilt artifacts and execute the benchmark gate. The release-only preflight is intentionally non-applicable.

## Evidence and limitations

The historical 912b309 qualification, d0e8085 qualification and third-remediation partial/escalation records are preserved under distinct filenames; latest qualifying artifacts describe the measured candidate only. Generated docs-only follow-up commits do not change source/tests/tools/workflows/examples/metadata/license build inputs. No older or dirty execution is silently attributed to HEAD.

SOL-011 remains the existing low-severity recursive callback-count follow-up; it was not expanded or changed. Pydantic remains pinned at 2.13.4; Python 3.11–3.14 and advertised OS lanes remain unchanged. This handoff does not promise arbitrary nested lifetime support, arbitrary tzinfo/objects, or publication.

Summary: two blockers addressed, two FIXED; zero partial/escalated/remaining blockers. Handoff: READY FOR SOL RE-REVIEW. No release was performed. Independent Sol approval remains required.

## Executed lane reconciliation

See [machine-readable execution evidence](../research/phase-0.3-final-execution.json) and [readable reconciliation](../research/phase-0.3-final-findings.md) for source-qualified commands, resolved dependencies, all 28 ACs and explicit non-applicability.

CI emits two nonblocking upstream Starlette/httpx/anyio deprecation warnings and an existing action-runtime Node 20 notice. These are recorded, not hidden or treated as release blockers; dependencies/workflows remain unchanged.
