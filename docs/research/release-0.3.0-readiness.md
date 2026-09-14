# 0.3.0 release readiness

Status: **native strings-ingress remediation verified locally; renewed review required**.

The independent final release check reopened SOL-017 as FINAL-001 on source
`5cb5587990ba96d535c9b970406b99e28aa4cabc`: native strings coercion could erase an
unsupported string subclass or enum before the closed-value audit. The current
[remediation investigation](phase-0.3-strings-ingress-investigation.md) records
the fix and its compatibility boundary. Earlier green gates below remain
historical evidence, not approval of this changed implementation. Normal
production review must PASS again before another independent final release check.

The following records describe the earlier preparation candidate:

No tag or publication was initiated. All preparation changes were committed and
pushed after local verification. The committed 0.3.0 candidate passed the complete
CI matrix; publication and final changelog dating remain separate actions.

## Prepared change

- Package metadata declares `0.3.0`; Python 3.11–3.14, exact Pydantic 2.13.4,
  MIT and development-only HTTP/build/static tooling remain unchanged.
- The versioned changelog describes scalar qualification, native/embedded ingress
  fixes, non-string `pop` migration and unchanged support limitations. Its date
  remains Unreleased until publication is explicitly initiated.
- README, documentation entry point and roadmap reflect Phase 0.3 independent
  review PASS and distinguish prepared source from published 0.2.0.
- Artifact metadata checking reads the actual source version at tool startup
  rather than hardcoding 0.2.0. Both wheel paths still assert exact installed
  version, package name, license and runtime dependency policy.
- Production source and every existing protected regression test are unchanged.
  The [independent review](../reviews/phase-0.3-rereview-5.md) verifies all 28 ACs
  and all 16 prior blockers. Its historical source identity is preserved.

## Verification and provenance

The committed release-preparation source
`c026ab857a3641803f7743722a4d33260470ffeb` passed
[CI run 34901690786](https://github.com/eddiethedean/pydandict/actions/runs/34901690786):
all eight compatibility, both artifact/benchmark and documentation jobs succeeded.
Every runtime lane passed 580 tests, strict positive/negative typing and 100%
public completeness. Actual interpreters were Linux 3.11.16/3.12.14/3.13.15/3.14.7,
macOS 3.11.9/3.14.7 and Windows 3.11.9/3.14.7. Both artifact lanes recorded version
0.3.0, 31 qualification commands, installed metadata and exactly four negative
typing diagnostics per wheel. Their source, hashes and actual outputs are retained
in [final execution](release-0.3.0-final-execution.json).
Release-only preflight was correctly skipped on this branch push.
The 46 measured components match the local source below; later documentation-only
closure does not relabel either measured source or its artifact hashes.

The final committed local candidate is
`7201c3f6ff59d82d8eeceabc4fb7ff346f901651`. Its refreshed README and 0.3.0
metadata passed fresh clean direct/rebuilt wheel qualification (31 commands).
[Final artifact measurements](release-0.3.0-final-artifacts.json) preserve actual
source, version, import paths, installed checks and dependency resolution.
[Final local execution](release-0.3.0-final-execution.json) records all 46 component
hashes, 580 passing tests in 101.12s, typing/lint/format/docs/README/HTTP checks and
the clean three-baseline/three-candidate benchmark. There is no numeric timing
ceiling. These fresh records supplement, not overwrite, the earlier snapshot below.

| Final local candidate artifact | SHA-256 |
| --- | --- |
| Sdist | `89d5cdbd0cbe80dedebb2e624800e1858b0b7ae375813262d8400a8267e3c2bc` |
| Direct wheel | `dfee560d1dc19587887434dd2a91063010002fa96fd27ad2afdf7b2d5fe3cd46` |
| Sdist-rebuilt wheel | `29621a121b341576608ef5c2667e890f0a2fc3d76a697abbc42fff5bdec55249` |

[Version-specific measurements](release-0.3.0-results.json) preserve full actual
commands, cwd/import paths, resolved dependency freezes, metadata/static outputs,
artifact hashes and a separate readiness annotation. Older Phase 0.2/0.3 evidence
was not overwritten or relabeled.

Fresh clean qualification used isolated detached snapshot
`6325b9f266878aa8d1ad25667cc80d17b40bb140` at
`/Volumes/T7/pydandict-release-030-fomOUr/checkout`.
That local verification commit is not a commit on main or a release tag.
All 48 preparation/runtime/test/workflow/example files compared equal to main's
prepared working-tree files. All 46 measured component hashes are recorded;
all source-module hashes also match the independently reviewed production.
Later documentation/evidence changes do not relabel the measured snapshot.

After these measurements, the README was refreshed with a user-facing quick start,
atomic updates, guarded descendants, serialization boundaries and support/migration
guidance. All seven README Python examples and FastAPI valid/invalid-request and
OpenAPI smoke checks pass; docs verification reports 56 Markdown files, 299 links,
11 Python examples and zero errors. The recorded snapshot/hash inventory contains
the earlier README, not this refreshed packaged long description. Requalify the
final committed candidate's artifacts in CI before tagging; the fresh local
qualification above now covers this README, while historical hashes and
source identities are intentionally unchanged.

| Gate | Actual result |
| --- | --- |
| Corrected full runtime suite on prepared main bytes | 580 passed in 109.24s |
| Focused protected provenance/evidence cases | 14 passed, original tests unchanged |
| Strict positive/exact negative typing | Passed on main and clean snapshot |
| Public type completeness | 100%, zero errors |
| Required Ruff lint/format inventory | Passed, 34 files |
| Clean-snapshot docs | 55 Markdown files, 316 links, eight examples, zero errors |
| Fresh 0.3.0 direct/rebuilt artifacts | Qualified, 31 actual commands |
| Bare installed scalar and nested workflows | Passed for both wheels, outside checkout, PYTHONPATH cleared |
| Installed HTTP, typing marker, positive/negative typing and completeness | Passed for both wheels; exact four negative diagnostics each |
| Installed name/version/MIT/exact runtime dependency metadata | Passed for both wheels |
| Retained build and archive inspection | Wheel/sdist built; Twine passed; wheel contains only package/typing/license/distribution metadata |
| Release tag/version/changelog preflight | Passed for proposed v0.3.0; no tag created |
| Private reporting / PyPI environment | Existing configuration verified, unchanged |

Local interpreter: CPython 3.11.14 on macOS 26.5.2 arm64. Fresh installed
dependencies include Pydantic 2.13.4/core 2.46.4, FastAPI 0.141.1, Starlette 1.6.0,
HTTPX 0.28.1 and Pyright 1.1.411; full per-environment freezes are in the record.
Python 3.11 libexec/bin and bin are first in PATH for detached static/artifact
execution. Local results are not an all-platform CI claim.

| Qualified snapshot artifact | SHA-256 |
| --- | --- |
| Sdist | `c8c88f2a06b9bbac39469ed8da29b69d6aebbf9c0d13657da15634396ce0d485` |
| Direct wheel | `a85f9c589c45b2d795ed4e9f5bfb747dff5057c2d619fb4010d4544235962297` |
| Sdist-rebuilt wheel | `c056f61109644421228a3f9d058baa62da9de30efb11df80f5ce5907e19ed434` |

The driver uses temporary artifacts/environments and records their measured
identities, not a claim that those files were uploaded. A separate retained
preparation build is available at
`/Volumes/T7/pydandict-release-030-fomOUr/artifacts`; it passed Twine/content
inspection but is not silently equated with the driver's separately built wheels.
The tag workflow must rebuild and qualify its own exact-source distributions.

## Failures addressed and remaining gates

The first full preparation run had one change-caused helper failure: the protected
provenance test intentionally redirects ROOT to a simulated project with no
manifest. Capturing the real tool source version at startup preserves that
unchanged test and exact installed-version checking. The focused and subsequent
complete run pass. No production test or required gate was weakened.

An initial jq summary failed, causing a broken output pipe; corrected execution
and final snapshot qualification pass. Default detached static execution selected
system python3 and could not resolve a pinned dependency symbol; explicit 3.11
PATH fixes it without source/configuration changes. An early snapshot commit
attempt raced the still-running worktree checkout; after checkout completed, the
isolated commit succeeded. Main/index/history were untouched. These attempts are
recorded rather than counted as passes.

At preparation time the PyPI 0.3.0 endpoint returned HTTP 404, and no remote
`refs/tags/v0.3.0` existed. Recheck immediately before publication.
The existing main-base [CI run](https://github.com/eddiethedean/pydandict/actions/runs/34897855014)
passed all 11 applicable jobs, but predates the 0.3.0 metadata/helper changes.
It is not CI approval of this new release-preparation source.

Still required for publication:

1. Explicitly initiate publication, finalize the changelog date and verify gates
   for that final commit before creating/pushing `v0.3.0`. The existing tag workflow
   additionally enables release-only preflight and validates tag/version equality.
2. After the explicitly initiated workflow publishes, verify installed PyPI
   artifacts and record the release result. Do not predeclare that verification.

There are no known release blockers, and committed-candidate CI is verified.
Historical follow-up issue #2 and editorial review
observations do not reopen the blocker loop; the README status observation is
resolved by this preparation.
