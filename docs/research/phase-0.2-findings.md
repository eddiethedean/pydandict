# Phase 0.2 evidence findings

This is implementation-side evidence for the nine Sol blocker fixes, awaiting
independent Sol re-review. The full measurement data, commands, source/artifact
hashes, exact dependencies and AC proof paths are in
[phase-0.2-results.json](phase-0.2-results.json). Per-finding root causes and
before/after verification are in [the remediation report](phase-0.2-remediation.md).
Historical prototype evidence and the approved plan remain unchanged.

## Source and qualification boundary

The measured candidate is the current Phase 0.2 implementation at commit
`7bf838325c462ceef66d32a2467ffafa40f938f2`, with the working-tree production
fix and review verification recorded explicitly in the source block. Benchmark
baseline is the unmodified production revision
`07fec9b7eafef5b00befe9fa24ccd012ce0232a1`; both revisions use the same
harness, Python and resolved dependencies.

Local runtime is macOS-26.5.2-arm64-arm-64bit, Python 3.14.3 and
Pydantic 2.13.4. This record does not assert current execution of the configured
Ubuntu/macOS/Windows matrix or Ubuntu 3.11/3.14 artifact lanes for this dirty
working-tree fix. The successful parent-source run
[34855996934](https://github.com/eddiethedean/pydandict/actions/runs/34855996934)
is retained as parent-source evidence; it does not qualify this unpushed
working-tree fix. The earlier
[historical CI run](https://github.com/eddiethedean/pydandict/actions/runs/34802350758)
remains explicitly pre-remediation.
Release dependencies remain `check -> build -> publish`; no publication or tag
was performed. Published 0.1.0 and unreleased Phase 0.2 facts remain separate.

## Contract and verification

The final base suite contains 147 passing tests, including the unchanged Sol
cases and implementation-side cases. The two new blocker contracts are executed
separately and fail for their expected reasons. The new cases cover completed typed extras, adapter
shape/rebuild behavior, unhashable model ingress, benchmark fixture invariants,
all before/after prepared swap positions and 500 discarded handles. Final gate
outcomes are recorded in the JSON and remediation report.

Strict Pyright covers all four source modules, the positive fixture and three
qualification helpers: eight files and zero errors. The independent negative
fixture produces exactly four expected rule/line errors. Configuration, analyzed
coverage, diagnostic multiplicity, exit status and fixture location are enforced.
Local and installed public type completeness is 100%.

Both direct and sdist-rebuilt wheels passed clean bare-library consumers and
HTTP/typing consumers in four separate environments. Runtime imports resolve
under each environment's site-packages, outside the repository. Each HTTP lane
checks successful requests, invalid 422 responses and OpenAPI. Each artifact
also executes its typing consumer, strict positive/negative checks, verifytypes
and py.typed checks. Artifact names/hashes and independent pip-freeze records are
retained in the JSON; the rebuilt wheel is exercised rather than merely hashed.

The supported annotation migration uses MutableSequence, MutableMapping and
MutableSet; ordinary input and serialized container shapes remain supported.
Explicit generic specialization, inherited/deferred typed-extra auditing,
immutable safe hash positions, ancestor-policy identity no-ops, detached copies
and guarded cache disposal agree with executable verification. The docs describe
the closed leaf whitelist and excluded hooks/adapters, without expanding scope.

## Measured performance

Three complete runs for each revision measure flat widths 10/100/1000/10000,
linear depths 1/5/20 and a mixed constrained sequence/mapping/set root: 50
applicable operation cells per run. Reads, scalar/nested edits, copies and Python/
JSON dumps run on every shape; the ten-field batch and rejected parent edit run
on the mixed constraint model. Other shapes explicitly mark those operations
inapplicable. Graph counts accompany each shape.

Every warmup, timed and allocation sample asserts state/results and root validator
counts. Each operation uses five warmups, at least 100 timed samples (10,000 for
reads), and ten separate traced allocation samples. Latency excludes tracemalloc
and verification. Full median/p95, allocation, validation and three-run variability
records are retained. These observed costs introduce no speed guarantee or budget.

Representative values below are medians of the three per-run medians/p95s; traced
peaks are medians of per-run median peaks, measured separately from latency.

| Shape/operation | Revision | Median ms | p95 ms | Traced median peak bytes |
| --- | --- | --- | --- | --- |
| flat_10000/scalar_write | baseline | 24.491 | 25.236 | 2414732 |
| flat_10000/scalar_write | candidate | 25.602 | 27.138 | 2463700 |
| linear_20/nested_leaf | baseline | 1.232 | 1.327 | 71840 |
| linear_20/nested_leaf | candidate | 1.878 | 2.041 | 65420 |
| mixed_parent/coupled_10field | baseline | 0.490 | 0.499 | 33480 |
| mixed_parent/coupled_10field | candidate | 0.597 | 0.649 | 33912 |

The linear fixture uses a distinct RootChain schema so recursive child validator
invocations are not counted as root invocations. A pre-existing duplicate invocation
when Chain is itself the root was reproduced on both revisions and recorded as a
follow-up candidate; no production change addresses it in this remediation.

## Acceptance-criterion trace

IMPLEMENTED reports implementation completion and local self-verification. Sol
owns independent AC verification and approval. Remote results are not fabricated.
The JSON contains concrete test/symbol/report paths for every row.

| AC | Implementation evidence status | Requirement |
| --- | --- | --- |
| AC-001 | IMPLEMENTED; local PASS | ABC fields, supported leaves, recursive and specialized models |
| AC-002 | BLOCKED; new Sol regression | An unrelated unresolved ClassVar can bypass deferred concrete-field rejection |
| AC-003 | IMPLEMENTED; local PASS | Closed input/output value and hash-position safety |
| AC-004 | IMPLEMENTED; local PASS | Configuration, namespace, hook and extra policies |
| AC-005 | IMPLEMENTED; local PASS | Nominal model/mapping identity and canonical public behavior |
| AC-006 | IMPLEMENTED; local PASS | Atomic coupled updates, failing generators and no-op operations |
| AC-007 | IMPLEMENTED; local PASS | Ancestor validation/freeze, unchanged state and recovery |
| AC-008 | IMPLEMENTED; local PASS | Canonical drift and retained topology rejection |
| AC-009 | IMPLEMENTED; local PASS | Public validation modes, strictness, aliases and context |
| AC-010 | IMPLEMENTED; local PASS | Adoption isolation, reorder identity and stale handles |
| AC-011 | IMPLEMENTED; local PASS | Exact identity no-ops, augmented assignment and ancestor policy |
| AC-012 | IMPLEMENTED; local PASS | Container/root and model/local iterator lifecycle |
| AC-013 | IMPLEMENTED; local PASS | Detached usable removals and preparation failure recovery |
| AC-014 | IMPLEMENTED; local PASS | Validated independent copies and guarded descendants |
| AC-015 | IMPLEMENTED; local PASS | Explicit-field/default/reset/cache and metadata lifecycle |
| AC-016 | IMPLEMENTED; local PASS | Stable diagnostics and propagated programming exceptions |
| AC-017 | IMPLEMENTED; local PASS | Checked compatibility adapter and class-local rebuild caches |
| AC-018 | IMPLEMENTED; local PASS | Serializer, alias, exclusion, schema and snapshot compatibility |
| AC-019 | IMPLEMENTED; local PASS | TypeAdapter/BaseModel/FastAPI request, 422 and OpenAPI integration |
| AC-020 | IMPLEMENTED; local PASS | Same-root reentry and BaseException recovery |
| AC-021 | IMPLEMENTED; local PASS | Every swap boundary rollback and guarded complete-state disposal |
| AC-022 | IMPLEMENTED; local PASS | Root retention/collection and bounded 500-replacement bookkeeping |
| AC-023 | IMPLEMENTED; local PASS | Complete strict private/source coverage and installed completeness |
| AC-024 | IMPLEMENTED; local PASS | Exact independent negative diagnostic multiset |
| AC-025 | IMPLEMENTED; parent-source CI PASS; current fix pending | CI matrix and release gate dependencies |
| AC-026 | IMPLEMENTED; parent-source artifact PASS; current fix pending | Direct/rebuilt isolated library, HTTP and typing consumers |
| AC-027 | IMPLEMENTED; current benchmark PASS | Actual baseline/current-tree benchmark with complete measurement protocol |
| AC-028 | BLOCKED; Sol re-review pending | Final evidence and AC trace are current-tree identified; independent approval remains pending |

## Remaining verification and follow-ups

The current benchmark and source hashes are reconciled. Current artifact
qualification for this unpushed fix remains unavailable locally because the
virtual environment has no pip/twine; parent-source artifacts are retained with
their source identity. Existing [issue #1](https://github.com/eddiethedean/pydandict/issues/1)
remains untouched. The recursive-root validator candidate is separate
pre-existing work for Sol triage.

NEEDS SOL RE-REVIEW
