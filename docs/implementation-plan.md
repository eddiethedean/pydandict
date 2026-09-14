# Implementation work packages

This backlog turns the [roadmap](../ROADMAP.md) into reviewable increments.
W01–W04 are demonstrated by the integrated Phase 0.1 prototype within its
[recorded envelope](research/prototype-findings.md), and W05's package scaffold is
now implemented at the repository root. Phase 0.2 finalizes those contracts and
hardens the baseline; the remaining W05–W13 qualification work stays open. IDs
remain stable references for issues and PRs.

The [Phase 0.3 implementation contract](phase-0.3-plan.md) defines the next bounded
W05 qualification/W06–W07 change, preserving the completed Phase 0.2 baseline.

## Priority and dependency order

**P0:** harden the integrated transaction/ownership baseline and finalize contracts
before committing to production internals. **P1:** deliver and qualify the supported core.
**P2:** improve adoption and cost after correctness, with no public scope expansion.

| ID | Priority / phase | Depends on | Deliverable | Acceptance |
| --- | --- | --- | --- | --- |
| W01 | P0 / 0.1 | Planning baseline | Complete model/mapping bridge spike and type fixtures | G1: key iteration, all mapping signatures, custom serialization, schema and real HTTP paths; no broad typing suppression |
| W02 | P0 / 0.1 | Planning baseline | Candidate transaction experiment and validator/hook compatibility report | G2: coupled writes, failure rollback, unchanged-value stability, aliases, defaults, fields-set, copy, freeze and context policy |
| W03 | P0 / 0.1 | Planning baseline | Ownership experiment using the W02 candidate interface | G3 feasibility: list/dict/set and child model, saved handles, root constraints, in-place writeback, return values, rejection of unsupported graphs |
| W04 | P0 / 0.1 | W01–W03 | One integrated vertical slice and architecture decision | Same nested model passes mapping consumer, transaction, strict typing, dump/schema and FastAPI checks; isolated spikes alone cannot pass |
| W05 | P1 / 0.1–0.3 | W04 | `src` package, `pyproject.toml`, `py.typed`, test tooling, CI, chosen license | G5 and initial G4: build/install from clean artifacts, minimal runtime dependencies, version bounds and reproducible development environment |
| W06 | P1 / 0.3 | W05 | Scalar reads and namespace policy | T2 plus read-side T6/T9/T10: canonical keys/order, extras, live views, iterator invalidation, ABCs and signatures |
| W07 | P1 / 0.3 | W06 | Production transaction engine and full scalar mutation API | T3–T6/T10: every mutator, frozen/error precedence, metadata, copies and inherited-path audit; unsupported mutable inputs rejected |
| W08 | P1 / 0.4 | W07, W03 | Production ownership integrated through the adapter | T7: complete method/escape inventory, identity, detached adoption, stale references, ancestor freeze and rollback |
| W09 | P1 / 0.4 | W08 | Full lifecycle and ecosystem matrix | T6/T8/T9/T10: construction modes, adapters, unions/generics, serializers, schemas, hooks and installed typing; finalize G1–G4 for this envelope |
| W10 | P1 / 0.4–0.5 | W09 | Robustness suite, measured baseline and regression budgets | T11 plus stateful/fault-injection qualification; collect initial timings at W04 and W07; freeze justified numeric budgets before beta |
| W11 | P1 / 0.5 | W09 | Three runnable guides, API/migration docs, two isolated automated consumer projects | T9/T12 and quality-bar journeys; fix workflow failures and explain intentional differences; no external participants required |
| W12 | P1 / 0.6 | W10–W11 | Candidate evidence record and distribution rehearsal | All release checklist items pass on the candidate commit; 1.0 needs full qualification and recorded automated consumer results |
| W13 | P2 / after qualification | W10–W11 | Consumer-driven ergonomics or optimization proposal | Measured problem, contract-preserving change, relevant tests and new benchmark results; separately decide any public API addition |

W01–W05 now share one working implementation. Their feasibility evidence does not
close the production release gates. Phase 0.2 is the hardening/finalization follow-up
to W04/W05; reuse the prototype regression corpus and working mechanisms while
qualifying the root package. No additional people or agents are required.

## Baseline experiment sequence

Phase 0.1 followed this sequence; retain it as context for the evidence.
The original W01 and W02 plan began with the recorded upstream probes as controls. Preserve those
controls instead of retroactively treating them as implementation tests. Put new
experiments in clearly named prototype files and save their actual output.

The first transaction fixture is a scalar `low <= high` model with a defaulted,
aliased field and explicit-field metadata. Exercise both write syntaxes, a coupled
update, a late generator error, and a validator exception. Add an unchanged-field
normalizer to make repeated transformation visible. Describe which validator
contracts work and why; do not hide unsupported behavior by weakening assertions.

Then add one list and one nested DictModel under a parent invariant. Carry that
same fixture through serialization and FastAPI in W04. Expand to the full W03
inventory before promoting the ownership design. This order exposes integration
failures before the team spends effort polishing a scalar-only implementation.

## Questions carried into Phase 0.2

The [Phase 0.2 implementation contract](phase-0.2-plan.md) resolves the target
decisions for these questions and defines their observable acceptance criteria.
The table below preserves the questions and experiment rationale; it does not
leave architectural choices open for the Phase 0.2 implementer.

| Question | Required experiment / decision |
| --- | --- |
| Can canonical stored state be revalidated? | Compare supported idempotent validators with representation-specific and non-idempotent controls; document drift, hook calls, and rejection limits. Arbitrary validator semantics cannot be inferred automatically. |
| Can transactions commit without executing user code? | Inject failures in input staging, candidate validation, guard preparation and reconciliation. Verify old values, metadata, handles and caches survive. Audit finalizers and callbacks around old-state disposal. |
| How do retained nodes survive full-root validation? | Specify identity transfer without invoking user equality/hash callbacks; test reorder, replacement, union branch changes and validator-created containers. |
| What do mutators return after removal? | Resolve `pop`/`popitem` of mutable values without returning unusable stale handles; prepare detached results before committing. See the proposed removal contract in nested values. |
| What happens to borrowed references after the root dies? | Select strong-root retention or an explicit orphan error; prove garbage collection of unreachable ownership graphs and absence of unbounded handle bookkeeping. |
| Can declared container APIs remain honest? | Runtime reads/equality/repr, strict type fixtures, standard serializers, ordinary copy/slice operations and mutation-return tests must agree. |
| Can a rejected operation leave future writes usable? | Follow every injected failure with a valid transaction; cleared reentrancy guards and intact ownership must allow success. |

The [findings](research/prototype-findings.md) record the current answers to these
questions. Phase 0.2 reviews their production consequences and remaining limits.
Record finalized behavior in the authoritative API, mutation, ownership and decision
documents. A prototype report must include counterexamples and exclusions, not just
successful demonstrations. G3 has a feasibility review at W04 and a production
qualification at W09; the first does not close the second.

## Definition of done for a work package

- Observable behavior matches the authoritative contract, with relevant R, I, T,
  and gate IDs in the PR description.
- Positive, rejection, and recovery paths are tested where state changes; assertions
  include ownership and metadata whenever affected.
- Public type and documentation changes agree with runtime behavior. No skipped
  required case or unresolved expected failure stands in for gate evidence.
- Any private upstream access has a reason, supported version range, dedicated
  adapter test, and removal path if a public upstream hook becomes available.
- The evidence record identifies the exact commit and commands. Unfinished scope
  remains visible in a follow-up item and blocks dependent work when necessary.

## Stop and revise criteria

Stop promotion to production internals if W04 needs a second writable state store,
an unguarded mutable fallback, hidden `Any`, serialized transaction inputs, or
repeated per-field assignment to simulate bulk atomicity. Those conflict with
established requirements. Record the failing case and compare designs before
continuing; do not accumulate workarounds behind an unchanged API promise.

If a supported schema cannot be isolated, a stale reference can mutate live state,
or Pydantic updates require scattered private patches, reopen the affected gate.
A scalar alpha remains possible only with a truthful scalar support boundary;
it does not fulfill the nested lifetime requirement for 1.0.
