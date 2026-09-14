# Phase 0.3 — Fifth independent production re-review

Reviewed 2026-09-14 against the [approved contract](../phase-0.3-plan.md), retained
Phase 0.2 behavior, [previous review](phase-0.3-rereview-4.md),
[implementation report](phase-0.3-remediation-rereview-4.md) and
[execution reconciliation](../research/phase-0.3-embedding-execution.json).
Candidate: `a33bb49263082effe0883233ce0cf21d2db2ca98`, clean at entry.
Production remediation: `4bf376e73c29be66a152f9a4904669428bee36fd`.
Their production/test/tool/workflow/example/metadata components are byte-identical;
the candidate's additional changes are documentation and evidence only.

Every in-scope AC is VERIFIED. All previous blockers are VERIFIED FIXED, including
SOL-017. No substantive change-caused regression or failing required gate remains.
This review adds only this report: no production, tests, dependencies, workflows
or historical qualification records were changed. No commit, push, tag,
publication or issue closure was performed. No new failing test was justified.

## Acceptance criteria

Evidence combines implementation/root-cause inspection, an independent complete
580-case run, focused protected tests, bounded adversarial probes, fresh external
artifact qualification, content/provenance audit and actual candidate CI logs.

| AC | Status | Verification |
| --- | --- | --- |
| AC-001 | VERIFIED | Native scalar/annotation modes, strictness and pinned BaseModel differentials, including embedded mixed strict date/coercing integer and strict strings. |
| AC-002 | VERIFIED | Original unsupported inputs and validator outputs are rejected; protected embedded subclass/attribute-source rejection now passes; inherited mutable guards remain supported. |
| AC-003 | VERIFIED | BaseModel/Mapping/MutableMapping identity, attribute/item agreement, canonical/default/excluded keys and extra ordering. |
| AC-004 | VERIFIED | Missing/non-string reads, membership/get, live views, empty models, dict/unpacking/pattern consumers without serializer calls. |
| AC-005 | VERIFIED | Iterator creation, before/after-first-next structural invalidation, value/failure/no-op stability and permanent exhaustion. |
| AC-006 | VERIFIED | Protected namespace, ambiguous aliases, canonical addressing and native alias/name options. |
| AC-007 | VERIFIED | Single attribute/item writes, value/model rejection, complete rollback and cache/metadata controls. |
| AC-008 | VERIFIED | Self/mapping/pair/keyword updates, duplicate precedence, coupled atomic changes and in-place identity. |
| AC-009 | VERIFIED | SOL-014 malformed-name precedence, non-string pop fallback, malformed pairs and late input failure/recovery. |
| AC-010 | VERIFIED | Existing setdefault ignores unused defaults; missing typed extras coerce; unknown ignore/forbid writes reject. |
| AC-011 | VERIFIED | Declared-removal protection, last-key popitem, empty/missing/fallback behavior and rejected fieldless-clear rollback. |
| AC-012 | VERIFIED | Selected defaults once, field-order factories, deduplication, metadata, required/extra/missing errors and exception recovery. |
| AC-013 | VERIFIED | Required/defaulted/nullable × policy × freeze controls, equal/mixed write rejection and specified no-ops. |
| AC-014 | VERIFIED | Detached extra/fields-set snapshots, explicit/reset/removal transitions, defaults and exclude-unset. |
| AC-015 | VERIFIED | Canonical Python/context=None, drift diagnostics and programming-exception propagation; native callback context is not retained by transactions/copies. |
| AC-016 | VERIFIED | Input/callback reentry, staging/prepared-swap/BaseException recovery, source isolation and completion-flag cleanup on compiler failure. |
| AC-017 | VERIFIED | Computed-cache success invalidation and failure/no-op identity preservation. |
| AC-018 | VERIFIED | Same-type independent validated shallow/deep/frozen copies, metadata, invalid updates and drift; recursive embedded source detachment also probed. |
| AC-019 | VERIFIED | Deprecated-copy warnings/partial-copy rejection, inherited validated paths and disabled construct/pickle controls. |
| AC-020 | VERIFIED | Class/TypeAdapter Python/JSON/strings options/context, detached existing inputs, ongoing extra policy and guarded ordinary-model/list embedding. |
| AC-021 | VERIFIED | Alias/exclusion/filter/context/custom serialization and JSON Schema controls; no engine-state leakage or mapping/serialization coupling. |
| AC-022 | VERIFIED | Direct model-not-dict equality, differing extras, mutable unhashability and frozen scalar BaseModel hash parity. |
| AC-023 | VERIFIED | Strict positive typing, exact four negative rule/location diagnostics, public completeness 100%; both clean-wheel static paths also pass. |
| AC-024 | VERIFIED | Fresh direct/rebuilt wheels install externally; scalar example, name/version/MIT/runtime dependency/py.typed and nested/HTTP consumers pass. |
| AC-025 | VERIFIED | Actual eight runtime, two artifact and one docs candidate jobs succeed; component/node/AC-cell/source/command/version/hash evidence reconciles. |
| AC-026 | VERIFIED | Independent scalar and retained nested machines each execute 100 examples × 100 steps, deadline=None, derandomize=True. |
| AC-027 | VERIFIED | Entire retained suite and protected prior fixes pass; rebuilt recursive ordinary-model/list embedding preserves rejection, ownership and canonical mutation. |
| AC-028 | VERIFIED | Installed scalar example, scoped API/error/migration/support claims, Unreleased correction and source-qualified evidence; docs links/examples pass without claiming publication. |

## Previous blockers

| Finding | Status | Verification / root-cause inspection |
| --- | --- | --- |
| SOL-014 | VERIFIED FIXED | Protected update/reset key-precedence verification passes; staging/name-policy ordering retained. |
| SOL-015 | VERIFIED FIXED | All 46 recorded component hashes match; all 580 nodes match independent collection; every proof resolves and all 28 ACs have 11 reconciled executed/non-applicable cells. |
| SOL-016 | VERIFIED FIXED | Both newly built external wheel paths execute the actual scalar example and installed metadata assertions. |
| SOL-017 | VERIFIED FIXED | Unchanged embedded-ingress verification and every earlier native-mode blocker test pass; compiled root dispatch preserves guard reuse while rewritten canonical validators suppress it. |
| SOL-001 | VERIFIED FIXED | Retained annotation/generic/deferred completion and specialization verification passes. |
| SOL-002 | VERIFIED FIXED | Retained unsupported/unsafe hash-ingress verification passes. |
| SOL-003 | VERIFIED FIXED | Retained owned identity, source independence and ancestor-freeze verification passes. |
| SOL-004 | VERIFIED FIXED | Checked adapter shapes, class-local cache isolation and deferred/rebuilt schemas pass. |
| SOL-005 | VERIFIED FIXED | Strict required source/fixture inventory and exact negative diagnostics pass. |
| SOL-006 | VERIFIED FIXED | Fresh external direct/rebuilt qualification and both actual candidate artifact lanes pass. |
| SOL-007 | VERIFIED FIXED | Executable benchmark baseline/generator contracts retained and passing; both CI benchmark steps succeed. |
| SOL-008 | VERIFIED FIXED | Historical benchmark provenance controls pass; new measurements are not relabeled historical results. |
| SOL-009 | VERIFIED FIXED | Finalizer/disposal/prepared-swap/BaseException rollback and recovery verification passes. |
| SOL-010 | VERIFIED FIXED | Guard-before-input/callback reentry verification passes; root transaction engine retained. |
| SOL-012 | VERIFIED FIXED | Protected existing-model Python context and public JSON context verification passes. |
| SOL-013 | VERIFIED FIXED | Protected existing-model ownership and public strings callback isolation verification passes. |

### SOL-017 closure

The fix addresses the previous root cause, not merely its four symptoms. The
compiled public root is now json-or-python rather than an outer identity
function-after. Embedded model-shaped nodes can reuse that complete public
validator, so ordinary BaseModel and TypeAdapter collection envelopes no longer
lose the child Python input guard. Native JSON/strings branches still validate
native input before output installation; there is no error replay, unconditional
strictness, framework monkeypatch or serialization transaction input.

Canonical/alias/Python schema rewrites must not reuse that public validator.
`compile_validator` gathers model classes in the checked schema, temporarily
suppresses reuse and restores each original completion flag in finally. Its
TypeError/KeyboardInterrupt controls pass, followed by successful nested canonical
mutation. Compilation is synchronous; concurrency/thread-safety remains explicit
non-scope rather than a newly inferred compatibility promise. The preparation,
commit, ownership and copy implementation is unchanged by this remediation.

Protected fourth-review verification SHA-256 remains
`79526f011654109adc42ac14a625510906aa10d599e4858b2106ade2dd82b200`;
third-review verification remains
`a0bab3487285dc2b91a0d171c6f1064f69f9e1b82275beb587c9598ed0749bd0`.
All 33 Phase 0.3 protected/blocker/embedding-control cases pass independently in
0.28s, including the four previously confirmed embedded-ingress failures.

Additional bounded probes warm public/canonical caches, force model rebuild,
then check embedded native alias/name/extra options, strict strings and mixed
field-specific JSON strictness against controls, metadata, canonical writes and
copies. Rebuilt recursive models embedded in ordinary-model/list envelopes reject
original unsupported subclass/attribute sources and detach existing models,
metadata and mutable handles before subsequent canonical mutation. These probes
pass; they add no equivalent-permutation verification burden to implementation.
The previous architectural escalation is resolved by this verified boundary repair.

## Quality gates and evidence

| Gate | Independently observed result | Classification |
| --- | --- | --- |
| Full runtime suite | 580 passed in 102.88s | PASS |
| Focused Phase 0.3 protected/blocker/embedding controls | 33 passed in 0.28s | PASS |
| Bounded warm-cache/rebuild/recursive probes | Passed | PASS |
| Strict typing | Positive and exact negative inventory passed | PASS |
| Public completeness | 100%, zero errors | PASS |
| Required Ruff lint/format inventory | Passed, 34 files formatted | PASS |
| Candidate docs | 54 Markdown files, 304 local links, eight examples, zero errors | PASS |
| Fresh external direct/rebuilt artifacts | Qualified; 31 actual commands, both installed metadata/negative gates pass | PASS |
| Exact-HEAD CI | All 11 applicable jobs succeed; eight runtime logs each report 580 passed and typing/completeness success | PASS |
| Whitespace/source identity | Passed; production unchanged by review | PASS |

Commands: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src python -m pytest -q`;
the same environment for the six Phase 0.3 protected/control test files;
`python tools/check_typing.py`;
`PYTHONPATH=src python -m pyright --verifytypes pydandict --ignoreexternal`;
CI's exact Ruff check/format inventory; `python tools/check_docs.py`;
`git diff --check`. Local CPython 3.11.14, macOS 26.5.2 arm64,
Pydantic 2.13.4/core 2.46.4 and Pyright 1.1.411.

Fresh qualification uses the unmodified driver in a detached exact-candidate
checkout at `/Volumes/T7/pydandict-sol-fifth-8E91Rn/checkout`, with Python 3.11
libexec/bin and bin first in PATH, external TMPDIR and the retained external pip
cache. The driver clears PYTHONPATH and installs outside the checkout. Its raw
record is that checkout's `docs/research/phase-0.3-results.json`, retaining real
argv/cwd/import paths, dependency freezes, scalar example and metadata outputs,
exact four negative diagnostics per wheel and artifact hashes. Main's older
results/findings remain untouched. Fresh bare consumers require only Pydantic
and its transitive dependencies; HTTP/static tooling remains separate.

[Exact-candidate CI](https://github.com/eddiethedean/pydandict/actions/runs/34897855014)
is independently confirmed completed/success. Actual logs, not just metadata,
confirm every runtime lane and both artifact records. Both benchmark steps also
succeed. Release-only preflight is correctly skipped on push, not a missing phase
qualification gate or evidence that a package was published.

| Candidate job | Actual CPython | Result |
| --- | --- | --- |
| Documentation checks | 3.11.16 | Passed |
| Ubuntu 3.11 runtime | 3.11.16 | Passed |
| Ubuntu 3.12 runtime | 3.12.14 | Passed |
| Ubuntu 3.13 runtime | 3.13.15 | Passed |
| Ubuntu 3.14 runtime | 3.14.7 | Passed |
| macOS 3.11 runtime | 3.11.9 | Passed |
| macOS 3.14 runtime | 3.14.7 | Passed |
| Windows 3.11 runtime | 3.11.9 | Passed |
| Windows 3.14 runtime | 3.14.7 | Passed |
| Ubuntu 3.11 artifacts | 3.11.16 | Passed |
| Ubuntu 3.14 artifacts | 3.14.7 | Passed |

| Fresh candidate measurement | Sdist SHA-256 | Direct wheel SHA-256 | Rebuilt wheel SHA-256 |
| --- | --- | --- | --- |
| Local 3.11.14 | `250dbf5a11eab0c6190ad8c37189669a83282a10235c6a6a7d1c5eb710397e59` | `139e19b9928a81d2fa4da8cbcb0a0cc98d5a859c169369b57a8a33890a984240` | `31bbebbb438eafa7fa05feed54afb48a000a6757bb786f89c89b0b850bb0bfca` |
| CI 3.11.16 | `6897a79936d38a822b15a62c7b6c203ac9ee06a9a3e36d49d73c1f4c668450f2` | `9470c3e2670610b6220728dbe084647477a439f4cf935de8f138a5d433a4b02f` | `62f6a82be3700a8f3b3b278914993c30129636139df72c3ba2242d15183dae5e` |
| CI 3.14.7 | `7abbf1dc8003a9339c18c7979e6279d6bb638a30484be93df67367e3768d8d73` | `8bdd0d9d760ca5d869a9818762756ae992fd22a3dc72840d089be6e34b2cd952` | `55f317204bc439a9a111234c0bc390f9b35e593f45aaaad6fa192e27a9fde9a8` |

The existing execution reconciliation correctly identifies production `4bf376e`,
not candidate `a33bb49`. All its 46 component hashes match candidate bytes, its
580 nodes exactly match fresh collection, every original/additional AC proof node
resolves, and its 11 passed job references resolve to real successful
[production-candidate jobs](https://github.com/eddiethedean/pydandict/actions/runs/34897109410).
All 28 × 11 cells distinguish actual execution from reasoned non-applicability;
behavioral exclusions separately describe non-representable Python objects/null
strings, closed timezone/annotation boundaries, applicable rejection/no-op cells
and unsupported exact callback counts. Command-only static/artifact/docs proof is
not falsely represented as pytest nodes. Prior failed/non-qualifying records and
their source identities remain preserved, not relabeled passing current results.

No required gate failed. Two exploratory assertions were over-prescriptive, not
release failures: an ongoing extra-allow model normalizes ignored extras to an
empty dictionary rather than a control's None, already present on the previous
reviewed candidate; alias-only existing-model revalidation needs applicable name
flags, and pinned BaseModel itself rejects canonical instance fields without them.
Corrected contract-level probes pass. Initial evidence queries also assumed arrays
where records use keyed objects and exceeded display limits; corrected hash/node/
job-reference audits succeed without modifying records or weakening verification.
Existing upstream deprecation/version notices do not fail required gates.

Final verification including this report: 55 Markdown files, 308 local links,
eight examples, zero errors; whitespace verification passes. The only main
worktree change is this untracked review report. All production components and
protected verification remain unchanged.

## New blockers

None. No blocker verification is left failing or handed to implementation.

## Follow-ups

| Finding | Severity | GitHub status |
| --- | --- | --- |
| SOL-011 — Historical repeated recursive root after-validator invocation | Low | EXISTING ISSUE [#2](https://github.com/eddiethedean/pydandict/issues/2), OPEN |

Disposition: FOLLOW-UP. Related AC: NONE. Location: recursive schema layering in
`src/pydandict/_core.py`, and `tools/benchmark.py` recursive fixtures.
The issue preserves the historical baseline differential, reproducer, expected
behavior and suggested broader verification. It is pre-existing callback-count
work, not a promised exactly-once AC. Current local execution of its reproducer
now reports one root after call for append and one for validated copy, preserving
correct model state. This is an improvement, not independent all-platform issue
closure; broader investigation/status reconciliation can remain separate.
Open issues were searched; no duplicate issue or failing follow-up test was
created. No new worthwhile unrelated defect was confirmed.

## Observations

SOL-018 — Historical README checkout-status wording.

Severity: Low. Disposition: OBSERVATION. Related AC: NONE.
Location: `README.md` lines 21–24.
The historical released-0.2.0 paragraph still says the checkout matches that
release, while lines 36–39 correctly identify pending Unreleased Phase 0.3 work.
Clarifying the historical paragraph would make status vocabulary less confusing.
This sentence predates the latest remediation; actual candidate evidence and
Unreleased behavior/migration claims are explicit and correct. The plan already
separates general stale status vocabulary from release-blocking requirements.
This low-value editorial cleanup does not prevent safe changed behavior or
meaningful qualification, does not merit a separate issue, and is not handed to
implementation. No production or README edit was made during review.

## Convergence

Previous blockers resolved: all 16; SOL-017 newly verified closed since the last
review. Blockers remaining: zero. New blockers attributable to remediation: zero.
New follow-ups discovered: zero; one historical open follow-up retained with its
current reproducer improvement recorded. One nonblocking editorial observation.
The remediation loop has converged. No follow-up or observation enters remediation.

This verdict means the reviewed change satisfies its release contract, not that
the repository is globally bug-free or that publication has occurred/is authorized.

PASS
