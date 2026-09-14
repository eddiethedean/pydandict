# Upstream behavior and planning evidence

Recorded 2026-09-13. The repository was inspected before documentation work:
`eddiethedean/pydandict` was empty, with no files, commits, license, package metadata,
implementation, or existing contributor rules. The remote is
[the user's repository](https://github.com/eddiethedean/pydandict).

The full referenced design conversation was read. Later decisions supersede its
early exploratory names, built-in-dict inheritance, `TypedMap`, and conversion
helpers. Its settled commitments are recorded as D01–D06 in the
[decision log](../decisions/README.md).

## Reproducible local baseline

The recorded environment is Python 3.11.14, Pydantic 2.13.4, FastAPI 0.141.1,
httpx 0.28.1, and Pyright 1.1.411. These are observed installed versions. No
assertion is made that this is the newest available stack or Pydandict's eventual
supported matrix.

Run [the upstream probe](../../tools/probe_upstream.py) and
[the typing fixture](../../tools/probe_typing.py) using the commands in
[CONTRIBUTING.md](../../CONTRIBUTING.md). The baseline output is saved in
[upstream-baseline.json](upstream-baseline.json).

| Observation tested | Design implication |
| --- | --- |
| Ordinary BaseModel iteration yields pairs and is not Mapping recognition | Mapping iteration needs an intentional override |
| A failed after-model assignment validator leaves the attempted value installed | `validate_assignment` is insufficient for rollback |
| Frozen model list and RootModel dict descendants remain directly mutable | Ownership is needed for a lifetime guarantee |
| `model_copy(update=...)` and `model_construct` accept unchecked values | Public copy/construction paths need an explicit safety policy |
| Defaults can remain unvalidated under default configuration | Require validation of defaults for the proposed safe contract |
| Extra-ignore construction drops unknown input; validated assignment rejects it | Document construction versus mutation policy |
| Raw mapping, serialized fields, and explicit-field metadata differ | Do not use dumps or full candidate input to infer live state/fields-set |
| TypeAdapter validates TypedDict input but later dict mutation is unchecked | Boundary validation is a different lifecycle abstraction |
| Minimal BaseModel/MutableMapping bridge supports key reads, dumps, and schema | Runtime inheritance direction is plausible |
| Minimal bridge parses a FastAPI body, returns a response, rejects invalid input, and appears in OpenAPI | Basic framework recognition works in this narrow experiment |

The strict Pyright fixture checks attribute type `int`, mapping read type `object`,
key-iterator type, and assignability to BaseModel/Mapping/MutableMapping. It uses
one documented iterator-override suppression because the two bases' iterator
contracts disagree. It is not evidence of field-specific literal-key inference.

Recorded validation: all ten upstream observation groups passed, and the strict
typing fixture reported zero errors and zero warnings. The documentation checker
verified 19 Markdown files, 81 local links, and five Python examples with zero
errors. Python examples were syntax-checked, not executed as Pydandict programs.

The bridge disables mapping writes and has **no transactional or nested ownership
implementation**. These results do not close G1–G3: custom serializers, nested
guards, complete APIs, lifecycle methods, broad typing fixtures, and dependency
matrix coverage still require actual Pydandict work.

## Primary reference register

The documentation links below were reviewed for this planning set. `/latest/`
pages move over time; reproduce claims using the recorded versions and rerun the
probes when upgrading. Design recommendations in this repository are our proposed
contracts, not statements that upstream already behaves that way.

| Source | Used for |
| --- | --- |
| [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/) | Model identity, RootModel, construction, copies, frozen/nested distinctions |
| [Pydantic configuration](https://docs.pydantic.dev/latest/api/config/) | Assignment/default validation, extras, frozen and instance revalidation controls |
| [BaseModel API](https://docs.pydantic.dev/latest/api/base_model/) | Copy/construct/validation entry points and model metadata |
| [Pydantic fields](https://docs.pydantic.dev/latest/concepts/fields/) | Required/default/nullable distinction, factories, aliases, computed fields |
| [Pydantic validators](https://docs.pydantic.dev/latest/concepts/validators/) | Modes, ordering, transformations, validation data/context |
| [Pydantic serialization](https://docs.pydantic.dev/latest/concepts/serialization/) | Python/JSON output, serializers, filtering |
| [Pydantic aliases](https://docs.pydantic.dev/latest/concepts/alias/) | Validation versus serialization naming |
| [TypeAdapter](https://docs.pydantic.dev/latest/concepts/type_adapter/) | Validation of types other than BaseModel |
| [Python mapping ABCs](https://docs.python.org/3/library/collections.abc.html) | Required mapping methods and mixins |
| [Python TypedDict](https://docs.python.org/3/library/typing.html#typing.TypedDict) | Static dictionary shape typing |
| [Pyright typed libraries](https://github.com/microsoft/pyright/blob/main/docs/typed-libraries.md) | `py.typed`, package completeness, library typing |
| [FastAPI request bodies](https://fastapi.tiangolo.com/tutorial/body/) | Pydantic request-model integration |
| [FastAPI response models](https://fastapi.tiangolo.com/tutorial/response-model/) | Response validation, filtering, serialization, schema |

Competitor primary package descriptions and their qualification are linked in the
[competitive landscape](../competitive-landscape.md). Their mutation guarantees
have not been independently tested by these probes.
