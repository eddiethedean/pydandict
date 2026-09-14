# Contributing to Pydandict

Pydandict is currently a planning repository. Start with the [README](README.md)
and [decision log](docs/decisions/README.md). There is no installable package or
implementation test suite yet.

## Work on the plan today

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

These pins describe the recorded probe environment, not the future package's
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

## Implementation workflow after M1

Follow the [roadmap](ROADMAP.md). The packaging milestone will introduce
`pyproject.toml`, a `src` layout, selected development dependencies, CI, and actual
test commands. Expected tools are pytest, Hypothesis, Ruff, and Pyright; exact
versions/configuration must be added with working code, not assumed here.

Keep version-sensitive Pydantic access isolated. Do not add custom validation,
serialization, persistence, or reactive frameworks. Safety-critical mutators need
meaningful failure-path tests, not only happy-path examples. Prefer public upstream
APIs; justify and test private access across the supported matrix.

Before a code PR is ready, run the relevant correctness/type checks, verify examples
against the built package when applicable, and update documentation for observable
changes. Before a release, complete the entire [release checklist](ROADMAP.md).

## Review checklist

- Does the change preserve one state for attribute and mapping access?
- Can any ordinary mutation, inherited method, or saved reference bypass validation?
- Do failures preserve values, metadata, ownership, and caches?
- Are field/default/extra/alias policies consistent across single and bulk operations?
- Are Pyright signatures honest about heterogeneous values?
- Are Pydantic/FastAPI behavior and deliberate differences tested and documented?
- Are support and performance claims backed by the stated evidence?

Use GitHub issues for ordinary design/bug discussion and pull requests for changes.
For potential vulnerabilities, follow [SECURITY.md](SECURITY.md). A license has not
yet been selected; do not assume this documentation commit grants redistribution
rights. License selection is a required pre-distribution decision.
