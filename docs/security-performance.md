# Security and performance considerations

## Trust boundary

PydanDict validates data supplied to trusted Python schemas and validators. It is
not a sandbox for hostile Python code, descriptors, custom validators, serializers,
or subclasses. Python reflection, direct base-method calls, and edits to private
storage can bypass normal object APIs. The lifetime contract covers supported
public operations and owned values under the documented validator requirements.

Do not evaluate schemas or import user-provided code from untrusted sources.
Validation errors can contain input values and sensitive data; applications must
control logging and error presentation. Preserve supported Pydantic redaction
configuration, and avoid adding raw state to library exception messages.

## Safety concerns and mitigations

| Concern | Design response | Verification |
| --- | --- | --- |
| Partial mutation after error | Isolated candidate, callback-free commit | Exception and rollback tests |
| Escaped nested references | Owned guards, detached inputs, root validation | Saved-reference and parent-invariant tests |
| Mass assignment / typo fields | Proposed default extra-forbid; restricted namespace | Unknown/protected key cases |
| Frozen field bypass through child | Ancestor freeze check on every nested write | Nested list/child tests |
| Unchecked copy/construct | Validated copies; disabled trusted construction | Public/deprecated path inventory |
| Serialization leaks | Keep ownership internals out of dumps/schema | Secret/exclusion/subclass filtering fixtures |
| Reentrancy | Reject same-root reentrant public transactions | Validator, generator, sort-callback cases |
| Cycles / excessive input | Detect cycles; document size/depth constraints | Adversarial graph and iterable tests |
| Supply-chain compromise | Minimal runtime dependencies and reviewed release process | Artifact/metadata checks and dependency review |

Mapping access exposes actual state. `Field(exclude=True)` is an output-serialization
rule, not read-access control; `dict(model)` may include that field. Callers handling
credentials should choose an explicit serialized response schema. Do not add a
second hidden mapping exclusion mechanism that contradicts field access.

`model_extra` metadata must not expose a mutable bypass. Private attributes are
outside the schema contract and must not independently control model invariants.
Readonly properties and serializers are trusted code: their external side effects
cannot be reversed by PydanDict.

## Resource use and concurrency

Atomic `update` must fully materialize its input. A huge or infinite iterable can
consume unbounded resources before validation completes. Applications should bound
request bodies, collection lengths, nesting depth, and operation sizes before or
through their schemas; do not invent silent truncation. A future explicit library
limit must have stable documented errors.

Use finite-tree ownership with cycle detection. Deepcopy is not a universal safety
primitive: custom objects can execute code, refuse copying, or preserve aliases.
Unsupported values should fail without entering live state.

V1 does not promise thread safety or concurrent transactions on one model. Use
external synchronization for shared writers/readers that require a consistent
snapshot. No async/await or I/O should occur inside a mutation transaction.
Validators should be deterministic, quick, and side-effect free. Revalidation
does not keep a model synchronized with time, databases, or other external state.

## Cost model

Target average constant-time field/key lookup and length, linear key iteration,
and lightweight view construction. Mutation is expected to be substantially more
expensive than dictionary assignment: candidate isolation and full-root validation
can scale with the owned graph size and user-validator cost, even for one changed
field. Peak memory may include both live and candidate graphs.

`update` should pay staging and validation cost once per batch. Schema construction
belongs at class setup, not on every assignment. Cache only safe structural metadata
such as field maps; do not cache validation results across changing state without
proof. Preserve correctness before attempting incremental validation.

## Phase 0.1 measurements

The [prototype report](research/prototype-findings.md#initial-costs) records initial
read/write timings, allocation samples and handle-retention checks. These are a
starting baseline, not the broader benchmark plan or production budgets below.

## Benchmark plan

The Phase 0.2 release measurements are recorded in
[phase-0.2-results.json](research/phase-0.2-results.json), with a
[readable findings report](research/phase-0.2-findings.md). They compare unmodified
production baseline `07fec9b` and candidate source on the same interpreter and
machine: flat sequences of 10/100/1000/10000 elements, linear chains of depth
1/5/20 and a mixed root with parent constraints. Each applicable operation has
three complete runs, correctness checks, median/p95 latency, separately traced
allocations and root-validation counts. There is no Phase 0.2 timing ceiling.
The broader workloads and beta budgets below remain future requirements.

| Workload | Variations | Measures |
| --- | --- | --- |
| Import and class creation | Cold import, inherited/generic models | Time and allocations |
| Construction | 5/50/500 fields; strict and coercing input | Latency, throughput, peak memory |
| Reads | Attribute, key, get, iteration, views, dict copy | Per-operation cost |
| Writes | One field, ten-field batch, rejection | Latency and validator call counts |
| Nested changes | Depth 1/3/10; small/large containers | Copy cost, root-validation cost, memory |
| Serialization | Python/JSON dumps and nested/custom serializers | Throughput and allocations |
| FastAPI | Matched request/response endpoints | End-to-end latency and output equality |

Compare plain dict, BaseModel with/without assignment validation, RootModel, and
TypeAdapter boundary validation. Label their different guarantees; a faster unsafe
mutation path is not equivalent functionality. Report Python/dependency versions,
hardware, dataset size, warmup, repetitions, and distribution statistics.

Establish budgets only after a measured baseline and representative library use
cases. Do not publish invented percentage overhead or speed claims. Investigate
material regressions against the same workload/environment; benchmark changes
must not bypass parent validators, defaults, or rollback to improve a number.

W04 records an early feasibility cost sample; W07 establishes the scalar baseline;
W09/W10 establish the supported nested baseline and numeric budgets before beta.
For each gating workload record input shape, expected behavior, measurement command,
baseline commit, machine/runtime, median and tail latency where meaningful, peak
allocation, repetitions, noise range, and allowed absolute and relative regression.
Select absolute ceilings using the library-config and FastAPI consumer workloads;
do not let a relative comparison hide an already unusable baseline.

Use repeated comparable runs to confirm a suspected regression before blocking
on timing noise. Budget changes need an evidence record and rationale, not an
automatic reset to a slower candidate. Keep small/medium/large graph measurements
to expose scaling changes, and measure batches against equivalent sequences of
valid single writes. Report validation invocation counts for both; do not promise
that Pydantic internally calls each validator exactly once.

Track cold import, direct/transitive runtime dependencies and wheel size alongside
latency. The proposed runtime dependency is Pydantic only; FastAPI, benchmarks,
documentation and testing tools stay outside the core installation. A new runtime
dependency requires a concrete need and measured cost, not just convenience.

Future optimization candidates include changed-path isolation and cached immutable
metadata. Any optimization must pass the full mutation/ownership contract before
it replaces the conservative implementation.
