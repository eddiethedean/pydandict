# Contributing to PydanDict

PydanDict starts at the integrated Phase 0.1 implementation. Start with the
[README](README.md), [package source](src/pydandict/__init__.py), [prototype guide](prototypes/README.md)
and [decision log](docs/decisions/README.md). The package is installable from PyPI
at `0.1.0` and in editable form for development. The release was built from the
matching tag and passed the release workflow checks. The checkout contains the
reviewed 0.2.0 release candidate; see the [release process](docs/release.md).

## Documentation and upstream controls

```sh
git clone https://github.com/eddiethedean/pydandict.git
cd pydandict
python3 tools/check_docs.py
```

The checker uses the standard library and checks local links, fragments, example
syntax, and code fences. Planned API examples are not executed. To reproduce the
upstream experiments in an isolated environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install pydantic==2.13.4 fastapi==0.141.1 httpx==0.28.1 pyright==1.1.411
.venv/bin/python tools/probe_upstream.py
.venv/bin/pyright tools/probe_typing.py
```

Use Python 3.11 or newer for the probes; ensure `python3` selects that interpreter
before creating the environment (or use `python3.11` explicitly).

These pins describe the recorded probe environment, not the package's broader
dependency bounds. Python 3.11.14 was used for the baseline. Probe classes are
deliberately incomplete and must never be shipped as the implementation.

## Design contributions

State the user-visible behavior, affected requirement/decision, tradeoff, and
acceptance evidence. If changing a proposed contract, update the authoritative
specification, examples, decision status, and test plan together. Preserve the
established BaseModel/mapping/lifetime goals unless the project explicitly revisits
them. New public APIs need a concrete use case within the narrow v1 scope.

Use small pull requests with a clear problem and resulting behavior. Link to the
relevant test group T1–T12 and note unsupported cases. A design PR can contain
experiments; label their limits. Do not claim a feature works because a minimal
prototype demonstrated one method.

## Run the production suite and historical baseline

Create a development environment, install the package, and run:

```sh
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest tests -q
.venv/bin/python prototypes/run_checks.py
```

The root test suite exercises the package. The prototype harness additionally builds
local artifacts and checks isolated consumers and installed typing; it records
source/artifact hashes and does not publish anything. Keep both suites passing during
Phase 0.2 hardening. The old `tools/probe_*` files remain separate upstream controls.

The [`ci.yml`](.github/workflows/ci.yml) entrypoint invokes the reusable
[`check.yml`](.github/workflows/check.yml) workflow for every push and pull request.

## Hardening workflow after 0.1

Follow the [roadmap](ROADMAP.md), [work packages](docs/implementation-plan.md),
and [quality bar](docs/quality-bar.md). W01–W04 provide the integrated feasibility
baseline and W05 packaging scaffold is now present; Phase 0.2 finalizes contracts
and hardens the implementation. Qualification uses automated consumer projects and
maintainer checks; no external trials or additional people are required. The package
uses pytest, Hypothesis, Pyright and Ruff for its development checks.

Keep version-sensitive Pydantic access isolated. Do not add custom validation,
serialization, persistence, or reactive frameworks. Safety-critical mutators need
meaningful failure-path tests, not only happy-path examples. Prefer public upstream
APIs; justify and test private access across the supported matrix.

Before a code PR is ready, run the relevant correctness/type checks, verify examples
against the built package when applicable, and update documentation for observable
changes. Name the work package and attach commit-specific evidence as well as
the relevant R/I/T references. Before a release, complete the entire
[release checklist](ROADMAP.md#release-checklist).

Release automation is documented in [docs/release.md](docs/release.md). The
workflow only accepts `vMAJOR.MINOR.PATCH` tags, runs the reusable checks first,
and publishes through PyPI Trusted Publishing from the tagged root package. The
development baseline is not a release artifact until its version and checklist gates
are complete.

## Review checklist

- Does the change preserve one state for attribute and mapping access?
- Can any ordinary mutation, inherited method, or saved reference bypass validation?
- Do failures preserve values, metadata, ownership, and caches?
- Are field/default/extra/alias policies consistent across single and bulk operations?
- Are Pyright signatures honest about heterogeneous values?
- Are Pydantic/FastAPI behavior and deliberate differences tested and documented?
- Are support and performance claims backed by the stated evidence?

Use GitHub issues for ordinary design/bug discussion and pull requests for changes.
For potential vulnerabilities, follow [SECURITY.md](SECURITY.md). The package is
licensed under MIT; private reporting, supported versions and release triage still
need to be configured before distribution.
