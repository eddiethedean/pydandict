# Nested values and ownership

## The lifetime requirement

Top-level assignment validation cannot protect `m.tags.append(...)`, a dictionary
obtained through `m['metadata']`, or a child model that is valid locally but breaks
a parent validator. The established requirement is continuous validation of
supported state changes. Deep mutation is therefore a release gate, not optional
marketing language.

The Phase 0.2 implementation uses **owned value trees with private mutation guards**.
External inputs are detached on adoption. Supported mutable descendants route
their writes to the root transaction coordinator. Immutable leaves may be shared.
This is implementation machinery for `DictModel`, not a separate collection API.

## Phase 0.1 implementation choice

The [prototype findings](research/prototype-findings.md) select private mutable ABC
handles with a single payload per node. Annotate fields with `MutableSequence`,
`MutableMapping` and `MutableSet` for matching runtime interfaces. Concrete
`list`/`dict`/`set` annotations still define validation schemas, but the prototype
returns protocol handles rather than instances of those built-ins. Full-root
serialization uses a raw snapshot to preserve Pydantic serializer behavior.

This resolves the unused-built-in-storage problem demonstrated by the experiments.
Phase 0.2 finalizes this scope refinement for the production API; concrete mutable
field annotations must migrate to the documented ABC interfaces. Ordinary input
and dump shapes are unchanged.

## Supported Phase 0.2 envelope

| Value | Implemented treatment | Boundary |
| --- | --- | --- |
| Exact safe scalar types | May share immutable identity | None, bool, int, float, str, bytes, Decimal, date/datetime/time/timedelta and UUID; datetime/time timezone is absent or exact datetime.timezone |
| Tuple / frozenset | Inspect descendants recursively | Tuples may contain owned descendants in value positions; hash positions require immutable safe descendants |
| MutableSequence / MutableMapping / MutableSet field | Private ABC guard with one payload | Ordinary list/dict/set inputs and serialized shapes remain supported; concrete mutable annotations are rejected recursively |
| Nested DictModel | Owned child associated with one root | Child mutation revalidates ancestor constraints; models/guards are forbidden in keys and set/frozenset members, even if frozen |
| Ordinary BaseModel, including frozen models | Reject | Frozen configuration does not prove deep immutability; migrate nested records to DictModel |
| Enum subclasses, arbitrary user objects, custom containers, iterators/resources | Reject | The scalar whitelist uses exact types; instance validation alone does not establish lifetime safety |
| Any / object / untyped extras | Inspect actual values on input and validator output | Broad annotations never bypass the safe envelope |
| Recursive schema with finite tree values | Supported within runtime recursion limits | Failure at runtime limits preserves existing owned state; no unbounded depth guarantee |
| Cycles / shared mutable inputs | Reject cycles; detach repeated mutable inputs independently | No shared-parent ownership protocol |

This is the implemented capability list. Mutable values without a safe guard,
including ordinary `BaseModel` instances and models in hash positions, are
rejected at ownership boundaries. Inputs are detached and validated before they
become public state.

## Identity and adoption

After adoption, `m.tags` and `m['tags']` return the same owned value/handle. They
must not return independent snapshots whose mutations disappear silently.
External input objects are not adopted by reference: changing the caller's original
list or child model must not change `m`.

When one mutable input appears in two fields, Phase 0.2 detaches
each occurrence into an independently owned value, with no alias-identity promise.
Detect true cycles and reject them with a clear error. Never recursively copy an
unbounded graph without cycle detection. Immutable leaves may retain identity.

A handle saved from a field remains attached across mutations to that same owned
node. Replacing or removing the node invalidates old handles; writes through them
raise a documented `RuntimeError` rather than modifying detached state silently.
Read access through stale handles must also raise, so callers cannot mistake them
for current model state. Container reordering must track node identity, not merely
an index path that could now identify a different child.

In a full-root transaction, reconciling candidate nodes with retained handles is
part of commit preparation. If guards cannot implement this safely, that is a G3
failure, not a reason to expose unguarded live storage.

Reconciliation must distinguish unchanged, moved, replaced and validator-created
nodes without trusting user equality or hash callbacks to establish identity.
Test a nested value moving to another index and a union changing branch. Validators
that reconstruct containers need an explicit handle-retention rule in the G3
report; do not silently attach a saved handle to a different equal-valued node.

Retained live handles keep their root alive. Releasing all external references
permits collection; the lifecycle tests check 500 subtree replacements and bounded
bookkeeping against the current reachable graph.

## Mutation inventory

The production mutation inventory covers these ordinary public methods:

- Lists: indexed/slice assignment and deletion, append, extend, insert, pop,
  remove, clear, reverse, sort, `+=`, and `*=`.
- Dictionaries: assignment/deletion, update, setdefault, pop, popitem, clear,
  `|=`, and values exposed by views/iteration.
- Sets: add, discard, remove, pop, clear, update, intersection/difference/symmetric
  difference updates, and their in-place operators.
- Nested models: attribute/key writes, every model mutator, copy/adoption, and
  mutations through descendants reached by either access syntax.

Sort key functions, iterables, equality operations, and user validators can raise
or reenter mutation. Stage their effects off the live graph. Ordinary non-mutating
operations may produce detached plain results, but must not leak writable raw
internals from the owned tree.

Python augmented assignment performs both an in-place operation and a subsequent
assignment (`m.tags += values`, `m['tags'] += values`). The guard/coordinator must
recognize its own already-committed handle writeback and avoid duplicate validation
or a second failure after the first commit. Test this specifically, including
frozen fields and self-referential operands.

## Parent constraints

Consider a root with `budget: int` and `costs: MutableSequence[int]`, constrained by
`sum(costs) <= budget`. Appending a valid integer can violate the root contract.
The operation must validate the candidate root, not only `list[int]` or its item
schema. The same applies to a child's valid field update that violates an ancestor
constraint or a discriminated union's active branch.

Frozen ancestors and frozen containing fields must block descendant mutation.
A child cannot evade that boundary by being mutable in its own class configuration.
For immutable aggregates, recursively owned mutable descendants still need guards
unless the aggregate is rejected by the safe envelope.

## Snapshots, copies, and escape paths

The removal-result contract: `pop` and `popitem` return a usable detached
value representing the removed value immediately before the operation. This applies
to allowed model extras and owned containers. Immutable leaves may be shared;
mutable containers are detached, and any returned DictModel becomes an independent
validated ownership root. Handles previously borrowed from the removed subtree
become stale as specified above; the return value is a distinct object when needed.
Prepare the detached result before commit so a copying/adoption failure leaves
the original root unchanged. A rejected removal returns nothing and invalidates
no handles. Identity with an earlier borrowed mutable value is not promised.

Test mutating the removal result, reading/writing the old handle, parent-constraint
rejection of removal, and a failure while preparing the detached result. Other
container operations returning values need the same explicit ownership analysis;
never make a successful `pop` return an immediately unusable stale handle.

`dict(m)` is shallow: nested values remain owned handles, and mutation through
those references still validates against `m`. It is not a detached editable payload.
Use serialization when a plain transferable payload is needed, subject to custom
serializer behavior. JSON output is the clearest detached boundary.

`model_copy` and `copy.copy` create a new ownership root. They may share
safe immutable leaves but must detach mutable descendants even when `deep=False`;
this is an explicit divergence from ordinary shallow BaseModel copies. `deep=True` uses the same detached ownership contract. Declared private attributes
are unsupported in Phase 0.2.
No copy may leave one child controlled by two independent roots.

Direct calls such as `list.append(guard, value)` on a list subclass can bypass an
overridden method, just as `object.__setattr__` can bypass model control. The
threat boundary excludes deliberate base-method/reflection bypass. Normal public
methods, metadata accessors, and ordinary consumers must remain protected.
Exact-type consumers and extension modules that mutate built-in storage directly
are outside the interoperability promise.

## Required G3 result

Deliver a documented supported-type table, ownership/identity tests, escaped-handle
tests, parent-invariant tests, JSON/schema/FastAPI results, and an inventory of
every ordinary mutator. Measure copying overhead. Do not promote a scalar-only
prototype into a general “dictionaries that stay valid” release without resolving
these requirements.
