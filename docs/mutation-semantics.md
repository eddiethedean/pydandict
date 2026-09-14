# Mutation semantics and invariants

This is the authoritative Phase 0.2 contract for mutations. No mutator may bypass
it by using an inherited ABC mixin or a raw Pydantic storage operation.

## Invariants

| ID | Invariant |
| --- | --- |
| I1 | After successful construction or mutation, owned state satisfies its supported Pydantic schema and validators. |
| I2 | `m.field` and `m['field']` refer to the same authoritative value. There is no second writable backing dictionary. |
| I3 | Every declared field is present; requiredness and default materialization are preserved. |
| I4 | Failure preserves all live field values, extras, key order, explicit-field metadata, ownership links, and relevant caches. |
| I5 | A bulk operation commits its complete validated result once, or commits nothing. |
| I6 | Supported reachable mutable values cannot change model state without a transaction, including through saved references. |
| I7 | A nested change satisfies the owning root's constraints, not just the child's local schema. |
| I8 | Serialization is observational: it does not define keys or provide transaction input. |

“Valid” means the contract actually enforced by the schema and trusted validators.
Pydantic permits user validators that replace or bypass normal validation; a
library cannot repair intentionally unsound user code or roll back its external
side effects. See [validator requirements](architecture.md) and the
[security boundary](security-performance.md).

## Single transaction

1. Resolve the operation and canonical keys; check existence and policy.
2. Materialize the complete input without changing the live object.
3. Create an isolated candidate from Python state, preserving explicit-field
   metadata separately. Do not serialize the model to construct this candidate.
4. Apply the complete operation to the candidate.
5. Run Pydantic validation and all applicable root/parent checks. Enforce frozen
   fields, ownership, namespace, and supported-value policy on the result.
6. Install the validated state and metadata with no further user callback.
7. Return the operation's specified result, using the committed/coerced value
   where appropriate.

If any pre-commit step raises, the live model must remain unchanged. Candidate
isolation must cover nested aliases, not just a shallow dictionary copy. “Atomic”
here means operation-level success/failure in supported single-threaded use; it
does not promise a database transaction or concurrent-reader isolation.

## Field and key policy

| Key/value category | Set / update | Delete / pop | Reset |
| --- | --- | --- | --- |
| Required declared field | Validate candidate | Reject | Reject: no default |
| Defaulted declared field | Validate candidate | Reject | Evaluate default/default factory and validate candidate |
| Nullable field without default | Accept `None` if schema permits | Reject | Reject: nullable is still required |
| Nullable field with `None` default | Validate candidate | Reject | Restore validated `None` |
| Allowed extra | Validate according to extra-value annotation, then ownership policy | Remove and validate remaining model | Reject: not a declared field |
| Unknown key, `extra='forbid'` | Reject | Missing-key rules | Missing-key error |
| Unknown key, `extra='ignore'` | Reject mutation | Missing-key rules | Missing-key error |
| Computed/private/protected name | Reject mapping write | Not a mapping entry; missing-key rules | Reject |
| Frozen field / frozen model | Reject writes affecting it | Reject | Reject |

The base default is `extra='forbid'`. During **construction**, explicit
`extra='ignore'` drops unknown input and `extra='allow'` stores accepted extras,
using Pydantic's configuration. During **mutation**, ignore does not silently
discard a misspelled write; this follows the assignment-oriented distinction
observed in the [baseline probe](research/upstream-behavior.md). Single-key writes,
attribute writes, `update`, and `setdefault` share this rule.

Typed extras can constrain values via Pydantic's extra-value annotation. Untyped
extras impose no value-type restriction, but all accepted values must still meet
ownership safety. PydanDict does not invent a type constraint for an `Any` value.
One-off construction overrides must not leave stored extras inconsistent with the
instance's ongoing class policy; reject a conflicting result explicitly.

## Destructive operations and defaults

All declared fields stay in the mapping even if they have defaults. A successful
`del` must remove its key; silently recreating it from a default would violate that
expectation. Therefore deletion and popping are limited to extras.

`reset('timeout', 'retries')` omits those fields in a candidate, evaluates their
defaults in Pydantic field order, validates the complete result, and commits once.
Duplicate reset names are processed once in first-occurrence order. Missing names
raise `KeyError`; required or extra names cannot be reset. A default factory may
fail; that failure leaves state intact. Unrelated defaults are not regenerated.

Data-dependent factories receive the preceding validated candidate fields as
Pydantic defines. Factory and validator calls must not be retried automatically;
there is no promise to reverse external effects. Resetting a field does not
necessarily reproduce its original construction value.

`pop(key, fallback)` returns fallback only for an absent key, not for a protected
field. `popitem()` attempts the last key, without scanning for some other removable
key. `clear()` fails as a whole when declared fields exist; it never means “clear
extras” or “reset everything.” A fieldless model may clear its extras if its model
validators allow an empty result.

Successful removal of a mutable extra returns a detached usable value prepared
before commit; prior borrowed handles become stale. The same ownership rule applies
to supported nested removal operations. See the
[removal-result contract](nested-values.md#snapshots-copies-and-escape-paths).

## Bulk writes and coupled fields

Suppose a model requires `low <= high`. Moving from `(1, 3)` to `(5, 8)` must work
with `update(low=5, high=8)`, even though setting `low` alone would fail. This rules
out the default strategy of implementing `update` as repeated public assignments.

An input generator that yields one good item then raises must not partially modify
the model. Duplicate keys resolve before validation. Frozen-field checks apply
even if a supplied value compares equal to the stored value. Unchanged fields
must not drift through non-idempotent normalization; this is a G2 prototype gate.

`setdefault` on an existing key returns it without validating the unused default
or running validators. On an absent allowed key it returns the committed value
after coercion, not the raw input default. A no-op does not mutate a frozen model;
operations that request a write to frozen state do fail.

## Error precedence

First enforce call shape and materialize the input. Then check key existence and
mutation policy before candidate validation. Missing reads/deletes/pop retain
their ordinary missing-key behavior, including on a frozen model. A present
protected/frozen key reports the policy violation. Full-schema validation follows
Pydantic's ordering; do not promise to aggregate every independent policy error.

Attribute syntax translates missing-key errors to `AttributeError` as appropriate,
while validation failures retain the same validation structure as mapping writes.
Both access paths must have identical successful state transitions.

## Explicit-field metadata

Keep `model_fields_set` independent of the candidate's full raw input. A naive full
revalidation marks all supplied defaults as explicitly set and breaks
`exclude_unset=True`.

Implemented rules: preserve original explicit fields; add successfully assigned field
names; remove reset fields; add inserted extra names and discard removed extras
where the supported upstream version tracks them. Validation-induced changes in
unspecified fields do not automatically make them user-supplied. Nested changes
mark the containing field explicit at each ancestor. Freeze this behavior with
tests against normal Pydantic assignment where behavior is intended to match.

On failure, metadata is unchanged. On successful writes, invalidate computed caches
that can depend on changed fields; until dependency tracking exists, invalidate
all supported cached computed values. Arbitrary user caches require explicit
support rather than guessing which attributes are safe to retain.

## Public bypass audit

Validated `model_copy(update=...)` is required; Pydantic's unchecked copy must not
be used as the transaction validator. Phase 0.2 `model_construct` raises
`TypeError` with guidance to `model_validate`. Deprecated copy paths must either
route to the validated copy contract or reject unsupported arguments.

`model_extra` and `model_fields_set` should return detached containers with their
usual public return types, so mutating metadata views cannot bypass validation.
Private attributes are not schema state; validators may not depend on independently
mutable private state for the continuous guarantee. Deliberate writes to
`__dict__`, private Pydantic internals, or direct base-class methods are outside the
supported API and cannot be made safe against hostile Python code.
