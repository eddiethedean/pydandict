# Release automation

The release workflow is [`.github/workflows/release.yml`](../.github/workflows/release.yml).
It runs only for tags matching `vMAJOR.MINOR.PATCH`, calls the reusable
[`check.yml`](../.github/workflows/check.yml) workflow first with its
`require_package` preflight enabled, builds the tagged source, and publishes the
exact wheel and sdist artifacts to PyPI.

The workflow builds the Phase 0.1 package from the repository root:

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

- `pyproject.toml` declares `pydandict` version `0.1.0`, MIT licensing, Python 3.11+
  and the pinned Pydantic 2.13.4 runtime.
- The root test suite, strict Pyright checks, public completeness check, Ruff checks,
  documentation validation and artifact metadata checks pass locally and in CI.
- The changelog contains the versioned `0.1.0` entry, and the workflow accepts only
  a matching `v0.1.0` tag.
- The release tag points to commit `6bfbd6082b8157decffc1b58e00505c670f00bdc`.
- The [successful release workflow run](https://github.com/eddiethedean/pydandict/actions/runs/34797121742)
  completed the checks, artifact build and Trusted Publishing upload.

The repository's PyPI Trusted Publisher and `pypi` environment are configured. The
publish job grants only
`id-token: write` (and read-only contents access), uses no PyPI token secret, and
publishes through `pypa/gh-action-pypi-publish@release/v1`. Configure environment
protection rules in GitHub if a manual approval gate is desired; the workflow does
not require a second maintainer.

To release, confirm the package version and changelog in a commit on the intended
branch, push that commit, and create an annotated or lightweight tag such as
`v0.1.0` pointing at the same commit. The tag is immutable for the purposes of the
run: checks and artifacts are built from that tagged source. Do not reuse a tag for
a different commit or version. A corrected release gets a new version and tag.

The workflow does not create GitHub Releases or publish to TestPyPI. Test the full
build and consumer path locally with the release checklist in
[the roadmap](../ROADMAP.md#release-checklist) before pushing a release tag.
