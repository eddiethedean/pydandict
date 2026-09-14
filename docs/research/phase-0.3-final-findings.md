# Phase 0.3 — Executed qualification reconciliation

Source: `7476decadc479488c9ed14772e3b7719455817ae`. Production implementation: `d0e80850be769be2c85e7b1d1230b76cbeefcdc4`.
[Exact-candidate CI](https://github.com/eddiethedean/pydandict/actions/runs/34893263306) completed successfully: eight runtime, two artifact, one documentation jobs.
[Machine record](phase-0.3-final-execution.json) carries all 562 collected node IDs, 43 component SHA-256 values, real install resolutions/log proof, command inventories, per-AC executed cells and behavioral axes/exclusions.
[Fresh local artifact record](phase-0.3-results.json) carries the 31 actual isolated commands, dependency freezes, installed imports/metadata checks and all artifact hashes.
[Remediation handoff](../reviews/phase-0.3-remediation-final.md): SOL-015 and SOL-017 FIXED; READY FOR SOL RE-REVIEW, not publication approval.

## Actual advertised lanes

| Cell | Resolved CPython | Execution | Result |
| --- | --- | --- | --- |
| docs/ubuntu/3.11 | 3.11.16 | [job 104140883027](https://github.com/eddiethedean/pydandict/actions/runs/34893263306/job/104140883027) | Passed |
| runtime/macos/3.11 | 3.11.9 | [job 104140883240](https://github.com/eddiethedean/pydandict/actions/runs/34893263306/job/104140883240) | Passed |
| artifact/ubuntu/3.11 | 3.11.16 | [job 104140883331](https://github.com/eddiethedean/pydandict/actions/runs/34893263306/job/104140883331) | Passed |
| artifact/ubuntu/3.14 | 3.14.7 | [job 104140883394](https://github.com/eddiethedean/pydandict/actions/runs/34893263306/job/104140883394) | Passed |
| runtime/ubuntu/3.14 | 3.14.7 | [job 104140883415](https://github.com/eddiethedean/pydandict/actions/runs/34893263306/job/104140883415) | Passed |
| runtime/macos/3.14 | 3.14.7 | [job 104140883425](https://github.com/eddiethedean/pydandict/actions/runs/34893263306/job/104140883425) | Passed |
| runtime/windows/3.14 | 3.14.7 | [job 104140883448](https://github.com/eddiethedean/pydandict/actions/runs/34893263306/job/104140883448) | Passed |
| runtime/ubuntu/3.11 | 3.11.16 | [job 104140883523](https://github.com/eddiethedean/pydandict/actions/runs/34893263306/job/104140883523) | Passed |
| runtime/windows/3.11 | 3.11.9 | [job 104140883572](https://github.com/eddiethedean/pydandict/actions/runs/34893263306/job/104140883572) | Passed |
| runtime/ubuntu/3.13 | 3.13.15 | [job 104140883669](https://github.com/eddiethedean/pydandict/actions/runs/34893263306/job/104140883669) | Passed |
| runtime/ubuntu/3.12 | 3.12.14 | [job 104140883694](https://github.com/eddiethedean/pydandict/actions/runs/34893263306/job/104140883694) | Passed |

Every runtime job reports 562 passed, strict positive/negative typing success and 100% public completeness; lint/format steps also passed. Exact installations (including Pydantic 2.13.4, pydantic-core 2.46.4, FastAPI 0.141.1, httpx 0.28.1, pyright 1.1.411, Ruff 0.16.7 and each resolved transitive dependency) are captured per job rather than inferred from classifiers.
The release-only preflight is intentionally skipped for this normal push (require_package=false); its explicit non-applicability is recorded.

## AC inventory and proof scope

Each row resolves its pytest anchors against the actual collected node inventory. Command-only artifact/static/docs proofs are listed separately. Required runtime cells link the exact successful job; jobs that do not execute a criterion are explicitly non-applicable, with reasons. Behavioral non-applicability is separate from OS/job non-applicability.

| AC | Collected proof nodes | Executed job kinds | Additional proof / behavioral dimensions |
| --- | --- | --- | --- |
| AC-001 | 262 | runtime | native-leaf-entry; annotation-entry |
| AC-002 | 49 | runtime | annotation-entry |
| AC-003 | 14 | runtime | leaf-mapping-serialization-copy; local/manual-mapping-consumers |
| AC-004 | 14 | runtime | leaf-mapping-serialization-copy; local/manual-mapping-consumers |
| AC-005 | 9 | runtime | mapping-extras-and-structure |
| AC-006 | 59 | runtime | native-options |
| AC-007 | 42 | runtime | mapping-role-policy-freeze; leaf-mapping-serialization-copy |
| AC-008 | 29 | runtime | mapping-role-policy-freeze; local/manual-mapping-consumers |
| AC-009 | 42 | runtime | mapping-role-policy-freeze; mapping-extras-and-structure |
| AC-010 | 39 | runtime | mapping-role-policy-freeze; mapping-extras-and-structure |
| AC-011 | 38 | runtime | mapping-role-policy-freeze; mapping-extras-and-structure; local/manual-mapping-consumers |
| AC-012 | 53 | runtime | mapping-role-policy-freeze; mapping-extras-and-structure; leaf-mapping-serialization-copy |
| AC-013 | 30 | runtime | mapping-role-policy-freeze |
| AC-014 | 52 | runtime | mapping-role-policy-freeze; mapping-extras-and-structure; leaf-mapping-serialization-copy |
| AC-015 | 22 | runtime | callback-isolation |
| AC-016 | 34 | runtime | callback-isolation |
| AC-017 | 2 | runtime | Retained named contract controls |
| AC-018 | 20 | runtime | leaf-mapping-serialization-copy |
| AC-019 | 3 | runtime | Retained named contract controls |
| AC-020 | 342 | runtime | native-leaf-entry; annotation-entry; native-options; callback-isolation |
| AC-021 | 14 | runtime | leaf-mapping-serialization-copy |
| AC-022 | 1 | runtime | equality-hashing |
| AC-023 | 0 | runtime | tools/check_typing.py; pyright --verifytypes pydandict --ignoreexternal |
| AC-024 | 0 | artifact | examples/library_config.py (direct/rebuilt clean-wheel execution); installed metadata, nested, HTTP and typing consumers |
| AC-025 | 1 | runtime, artifact, docs | tools/qualify_package.py |
| AC-026 | 1 | runtime | Retained named contract controls |
| AC-027 | 9 | runtime | Retained named contract controls |
| AC-028 | 0 | artifact, docs | examples/library_config.py (direct/rebuilt clean-wheel execution); tools/check_docs.py |

Actual test anchors, fully resolved parameter IDs and per-cell job references are in the machine record; the [generated readable inventory](phase-0.3-findings.md) also lists every named anchor. The [handoff's behavioral table](../reviews/phase-0.3-remediation-final.md#behavioral-applicability) explains nullable strings, custom tzinfo, generic/concrete-mutable rejection, frozen/destructive operations, canonical Python/context=None, mutable hashing, and release-only job exclusions. Expected rejection cells are not relabeled as omissions.

Direct anchors added beyond the earlier broad map include iterator before/after-first-next transitions and permanent exhaustion, mutable/frozen hash and model/dict equality, scalar read/unpack/pattern consumers without serializers, cache failure/no-op identity, fields-set/extra snapshots, construction versus mutation/copy context, fieldless rejected clear, selected default-factory order/deduplication, malformed/late batches, typed-extra insertion/reset errors and inherited copy/parse/disabled APIs.

## Genuine local execution

Full suite: 562 passed in 114.18s on macOS 26.5.2 arm64 / CPython 3.11.14. Required lint/format (32 files), strict positive/exact negative typing, and public completeness (100%) passed. Candidate docs: 50 Markdown files, 274 local links, eight Python examples, zero errors; final handoff documentation is checked again before the documentation-only follow-up.
The independent scalar and retained nested stateful machines both execute max_examples=100, stateful_step_count=100, deadline=None, derandomize=True locally and in all runtime jobs.

An actual source-qualified inline Python probe also checks self update/in-place union return identity and metadata, BaseModel/MutableMapping identity, empty truth/length/views, empty popitem/missing pop errors and exact fallback-object identity. Its executable command and output are in local/manual_mapping_consumers; it is not attributed to an unrelated or older CI run.

## Artifact identity

The local direct and sdist-rebuilt bare-wheel environments execute the actual scalar library example without development dependencies or source injection, then check installed metadata, nested/HTTP consumers and exact installed typing diagnostics. CI artifact jobs repeat the real driver on their recorded interpreters and run the benchmark report gate.

| Measurement | Sdist SHA-256 | Direct wheel SHA-256 | Rebuilt wheel SHA-256 |
| --- | --- | --- | --- |
| Local CPython 3.11.14 | `44fabfcdd6794abc0d966512a2cc16da920978b38996b5d544306fb83ae6d29b` | `ceca3b3aa903c1a1be122abc200b80a6aa7e6945d1a8e5a310967f0e1c435f15` | `2e3e01b1e72625f938947d7847a5a1a4181ad3efe1779347408554b0fa187684` |
| CI CPython 3.11.16 | `5a9b29062e2359ce1c247482590951a30dae21dfcc1cc1ee6c6e2e7895bee420` | `d01d38ec4009c327c9916d367e18f0bcc963b3a5c230bc062f2a5527ef093678` | `2e0c5bfa640a9a68eddea2686d3b73a07254bf9a2f0063bdab0a296bdc3dd99e` |
| CI CPython 3.14.7 | `7209ff116b5cab8f249ff58d8f30bffa07302924937a2cce346764872bf145ff` | `d01d38ec4009c327c9916d367e18f0bcc963b3a5c230bc062f2a5527ef093678` | `d01d38ec4009c327c9916d367e18f0bcc963b3a5c230bc062f2a5527ef093678` |

Artifact hashes are measured per actual build, not required to be reproducibly equal across timestamps/environments. Exact working directories, build/install/example/consumer/static commands and freezes are in the records. Temporary qualification environments/artifacts were disposed by the existing driver; this is measured evidence, not a published package.

## Preservation, warnings and limitations

Earlier [912b309 qualification](phase-0.3-results-912b309.json), [d0e8085 qualification](phase-0.3-results-d0e8085.json), and [third-remediation non-qualifying/escalation evidence](phase-0.3-remediation-3-evidence.json) remain preserved separately. Dirty relevant-source or missing-provenance runs cannot replace durable qualified evidence; protected orchestration controls and new dirty-source checks pass.

CI's resolved Starlette 1.6.0 produces two nonblocking upstream httpx/anyio deprecation warnings. Local runtime Starlette 0.48.0 and fresh artifact/CI 1.6.0 paths were genuinely exercised. Existing actions receive a Node 20 deprecation notice and run with Node 24; no workflow/dependency expansion was made for unrelated warnings.
SOL-011 remains the existing nonblocking recursive callback-count follow-up. Custom tzinfo/arbitrary attribute objects, lossy JSON construction, arbitrary nested lifetime claims and publication remain outside this handoff.

The subsequent evidence/handoff commit changes documentation only. The measured candidate identity is retained explicitly; source/tests/tools/workflows/examples/README/metadata/license inputs remain byte-identical, verified before that commit. Its later CI can pass independently without silently replacing these measured source/artifact identities.

Summary: 2 blockers addressed, 2 FIXED, 0 partial/escalated/remaining. READY FOR SOL RE-REVIEW; independent approval still required.
