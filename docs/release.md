# Release automation

The release workflow is [`.github/workflows/release.yml`](../.github/workflows/release.yml).
It runs only for tags matching `vMAJOR.MINOR.PATCH`, calls the reusable
[`check.yml`](../.github/workflows/check.yml) workflow first with its
`require_package` preflight enabled, builds the tagged source, and publishes the
exact wheel and sdist artifacts to PyPI.

The workflow builds the production package from the repository root:

- `pyproject.toml` must declare project name `pydandict`.
- `src/pydandict/` must exist.
- The package version must equal the tag with its leading `v` removed. For example,
  `v1.2.3` requires `project.version = "1.2.3"`.

The Phase 0.1 package was released as version `0.1.0` on 2026-09-13. The matching
`v0.1.0` tag passed the reusable checks, built the wheel and sdist, and published
both artifacts to [PyPI](https://pypi.org/project/pydandict/0.1.0/). A future release
tag still stops in the reusable checks if metadata, tests or artifacts fail.

## 0.1.0 release record

The repository release gates are complete for the documented alpha envelope:

- The tagged `pyproject.toml` declares `pydandict` version `0.1.0`, MIT licensing, Python 3.11+
  and the pinned Pydantic 2.13.4 runtime.
- The root test suite, strict Pyright checks, public completeness check, Ruff checks,
  documentation validation and artifact metadata checks pass locally and in CI.
- The changelog contains the versioned `0.1.0` entry, and the workflow accepts only
  a matching version tag, including `v0.1.0` for that release.
- The release tag points to commit `6bfbd6082b8157decffc1b58e00505c670f00bdc`.
- The [successful release workflow run](https://github.com/eddiethedean/pydandict/actions/runs/34797121742)
  completed the checks, artifact build and Trusted Publishing upload.

## 0.2.0 release record

Version `0.2.0` was published on 2026-09-14 from the immutable [`v0.2.0` tag](https://github.com/eddiethedean/pydandict/tree/v0.2.0).
The release workflow run [34872713924](https://github.com/eddiethedean/pydandict/actions/runs/34872713924)
passed every required check, built both distributions, and completed Trusted Publishing.
The [published package](https://pypi.org/project/pydandict/0.2.0/) contains the
intentional alpha annotation/generic migration described in the versioned
changelog entry. Phase 0.2
[passed independent review](reviews/phase-0.2-rereview-6.md), with AC-001–028
verified, all release blockers resolved and exact-source CI successful. The
[Phase 0.2 evidence](research/phase-0.2-findings.md) preserves the actual measured
source and prior 0.1.0-metadata qualification. Private security reporting is enabled; the maintainer owns
triage as described in [SECURITY.md](../SECURITY.md).

The [0.2.0 qualification record](research/release-0.2.0-results.json) records fresh
direct/rebuilt artifact consumers and release-preparation gates separately from
the historical Phase 0.2 benchmark. It also records local interpreter failures
and the portability correction, rather than treating failed attempts as passes.

The release completed the complete checks and direct/rebuilt wheel qualification
before tagging. The tag-triggered workflow ran all required checks plus the
release-only preflight, verified version equality, built distributions and
published through the existing Trusted Publisher. No additional reviewer or
external trial was required.

## 0.3.0 release preparation

The checkout declares version `0.3.0`. Phase 0.3
[passed independent review](reviews/phase-0.3-rereview-5.md): all 28 ACs and all
16 previous blockers are verified resolved. The
[production evidence](research/phase-0.3-embedding-execution.json) and prior
review retain their measured source/version identities; they are not silently
relabeled 0.3.0 artifact qualification.

The versioned changelog records scalar qualification, non-string `pop` migration
and native/embedded ingress corrections. Python 3.11–3.14, the exact Pydantic
2.13.4 dependency, MIT and the existing nested envelope remain unchanged.

Before tagging this candidate:

- [x] Resolve every Phase 0.3 release blocker and complete independent review.
- [x] Prepare 0.3.0 metadata, versioned changelog and accurate unpublished status.
- [x] Qualify new 0.3.0 direct/rebuilt wheels outside the checkout, including
  installed metadata, scalar/nested/HTTP consumers and static gates; see
  [local readiness and measured source](research/release-0.3.0-readiness.md).
- [ ] Verify the complete CI matrix on the committed release-preparation source.
- [ ] Explicitly initiate publication, finalize the changelog date and create
  `v0.3.0` at that verified commit. Do not move or reuse an existing release tag.

Creating and pushing the version tag triggers publication through the existing
workflow. No tag or publication is part of release preparation. The existing
`pypi` environment and private-reporting configuration must not be broadened just
to prepare a new version.

## Publishing a verified candidate

The repository's PyPI Trusted Publisher and `pypi` environment are configured. The
publish job grants only
`id-token: write` (and read-only contents access), uses no PyPI token secret, and
publishes through `pypa/gh-action-pypi-publish@release/v1`. Configure environment
protection rules in GitHub if a manual approval gate is desired; the workflow does
not require a second maintainer.

To release, confirm the package version and changelog in a commit on the intended
branch, push that commit, and create an annotated or lightweight tag such as
`v0.3.0` pointing at the same commit. The tag is immutable for the purposes of the
run: checks and artifacts are built from that tagged source. Do not reuse a tag for
a different commit or version. A corrected release gets a new version and tag.

The workflow does not create GitHub Releases or publish to TestPyPI. Test the full
build and consumer path locally with the release checklist in
[the roadmap](../ROADMAP.md#release-checklist) before pushing a release tag.
