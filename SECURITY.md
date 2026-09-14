# Security policy

PydanDict is an alpha package. Version 0.1.0 is published; 0.2.0 is prepared for
release. Security fixes target the latest published `0.x` series. Earlier alpha
series may require upgrading, and pre-1.0 fixes may include documented breaking
changes. See the [security design](docs/security-performance.md) for the validation
boundary.

Report potential vulnerabilities privately through
[GitHub Security Advisories](https://github.com/eddiethedean/pydandict/security/advisories/new).
Private vulnerability reporting is enabled. Do not post exploit details,
credentials or sensitive data in public issues. If the private channel is
temporarily unavailable, open a minimal issue requesting a private channel without
those details. No response SLA is promised.

Include affected versions/commit, environment, a minimal reproduction, the violated
invariant, and expected versus actual behavior. The repository maintainer owns
triage: reproduce the issue within the supported envelope, assess affected
versions, prepare and verify a fix, and publish a corrective release through the
tag-gated workflow. Coordinate disclosure through the private advisory and publish
an advisory when a confirmed vulnerability is fixed. Published artifacts and tags
are never replaced; unsafe releases may be yanked in favor of a new version.

PydanDict is intended to validate data under trusted schemas and validators. It is
not intended to contain hostile Python code, reflection, unsafe deserialization,
or deliberately overridden safety methods.
