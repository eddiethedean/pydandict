"""The narrow Pydantic compatibility boundary used by :mod:`pydandict`."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import pydantic

SUPPORTED_PYDANTIC_VERSION = "2.13.4"


def ensure_supported() -> None:
    """Fail closed when the pinned Pydantic storage/schema contract changes."""
    if pydantic.__version__ != SUPPORTED_PYDANTIC_VERSION:
        raise TypeError(
            "pydandict_incompatible_pydantic: expected "
            f"pydantic {SUPPORTED_PYDANTIC_VERSION}, found {pydantic.__version__}"
        )
    required = (
        "model_fields",
        "model_config",
        "__pydantic_core_schema__",
        "__pydantic_validator__",
    )
    if any(not hasattr(pydantic.BaseModel, name) for name in required):
        raise TypeError(
            "pydandict_incompatible_pydantic: required Pydantic model structures are missing"
        )


def fields(model_or_cls: Any) -> dict[str, Any]:
    return cast(dict[str, Any], getattr(model_or_cls, "model_fields"))


def config(model_or_cls: Any) -> Mapping[str, Any]:
    return cast(Mapping[str, Any], getattr(model_or_cls, "model_config"))


def raw_state(model: Any) -> dict[str, Any]:
    return cast(dict[str, Any], object.__getattribute__(model, "__dict__"))


def raw_extra(model: Any) -> dict[str, Any] | None:
    return cast(dict[str, Any] | None, object.__getattribute__(model, "__pydantic_extra__"))


def fields_set(model: Any) -> set[str]:
    return cast(set[str], object.__getattribute__(model, "__pydantic_fields_set__"))


def set_fields_set(model: Any, value: set[str]) -> None:
    object.__setattr__(model, "__pydantic_fields_set__", value)


def core_schema(model_or_cls: Any) -> Any:
    return getattr(model_or_cls, "__pydantic_core_schema__")


def validator(model_or_cls: Any) -> Any:
    return getattr(model_or_cls, "__pydantic_validator__")


def set_attribute(target: Any, name: str, value: Any) -> None:
    object.__setattr__(target, name, value)


ensure_supported()
