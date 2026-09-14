# Security policy

Pydandict is planning-only and has no released package or supported release series
at this time. See the [security design](docs/security-performance.md) for the
proposed validation boundary and release requirements.

For a potential vulnerability, use the repository's GitHub **Security → Report a
vulnerability** option if private reporting is available. Its availability has not
been configured or verified by this planning commit. If it is unavailable, open a
minimal issue requesting a private reporting channel without exploit details,
credentials, or sensitive data. No private email address or response SLA has been
established yet.

Include affected versions/commit, environment, a minimal reproduction, the violated
invariant, and expected versus actual behavior once a private channel is available.
Before the first distribution, maintainers must establish private reporting,
supported-version policy, triage ownership, and an advisory/release process.

Pydandict is intended to validate data under trusted schemas and validators. It is
not intended to contain hostile Python code, reflection, unsafe deserialization,
or deliberately overridden safety methods.
