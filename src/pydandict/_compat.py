"""The checked, version-sensitive Pydantic storage and schema boundary."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, TypeVar, cast

import pydantic
from pydantic import BaseModel, ConfigDict, GetCoreSchemaHandler
from pydantic.fields import FieldInfo
from pydantic_core import CoreSchema, SchemaValidator
from pydantic_core import core_schema as schema_tools

SUPPORTED_PYDANTIC_VERSION = "2.13.4"
M = TypeVar("M", bound=BaseModel)
SlotUpdate = tuple[object, str, object]


def _incompatible(message: str) -> TypeError:
    return TypeError(f"pydandict_incompatible_pydantic: {message}")


def ensure_supported() -> None:
    if pydantic.__version__ != SUPPORTED_PYDANTIC_VERSION:
        raise _incompatible(
            f"expected pydantic {SUPPORTED_PYDANTIC_VERSION}, found {pydantic.__version__}"
        )
    if any(
        not hasattr(BaseModel, name)
        for name in (
            "model_fields",
            "model_config",
            "__pydantic_core_schema__",
            "__pydantic_validator__",
        )
    ):
        raise _incompatible("required Pydantic model structures are missing")


def _string_dict(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or any(
        not isinstance(key, str) for key in cast(dict[object, object], value)
    ):
        raise _incompatible(f"{label} must be a dictionary with string keys")
    return cast(dict[str, Any], value)


def fields(cls: type[BaseModel]) -> Mapping[str, FieldInfo]:
    result = _string_dict(getattr(cls, "model_fields", None), "model fields")
    if any(not isinstance(field, FieldInfo) for field in result.values()):
        raise _incompatible("model fields must contain FieldInfo values")
    return cast(Mapping[str, FieldInfo], result)


def config(cls: type[BaseModel]) -> ConfigDict:
    return cast(ConfigDict, _string_dict(getattr(cls, "model_config", None), "model config"))


def raw_state(model: BaseModel) -> dict[str, object]:
    return _string_dict(object.__getattribute__(model, "__dict__"), "model storage")


def raw_extra(model: BaseModel) -> dict[str, object] | None:
    extra = object.__getattribute__(model, "__pydantic_extra__")
    return None if extra is None else _string_dict(extra, "model extra storage")


def fields_set(model: BaseModel) -> set[str]:
    result: object = object.__getattribute__(model, "__pydantic_fields_set__")
    if not isinstance(result, set) or any(
        not isinstance(key, str) for key in cast(set[object], result)
    ):
        raise _incompatible("model fields-set must be a set of strings")
    return cast(set[str], result)


def set_fields_set(model: BaseModel, value: set[str]) -> None:
    object.__setattr__(model, "__pydantic_fields_set__", value)


def _checked_schema(value: object) -> CoreSchema:
    schema = _string_dict(value, "core schema")
    kind = schema.get("type")
    if not isinstance(kind, str) or not kind:
        raise _incompatible("core schema lacks its required type")

    # Check the structures consumed by our rewrites, including wrapped models.
    def check(node: Any) -> None:
        if isinstance(node, dict):
            node = cast(dict[str, Any], node)
            if node.get("type") in (
                "model",
                "function-before",
                "function-after",
                "function-wrap",
                "nullable",
                "default",
                "definitions",
            ) and not isinstance(node.get("schema"), dict):
                raise _incompatible("core schema wrapper lacks its inner schema")
            if node.get("type") == "model":
                if not isinstance(node.get("cls"), type) or not issubclass(node["cls"], BaseModel):
                    raise _incompatible("model core schema lacks its model class")
                if not isinstance(node.get("schema"), dict):
                    raise _incompatible("model core schema lacks its inner schema")
                _string_dict(node.get("config", {}), "model schema config")
            if node.get("type") == "model-fields":
                model_fields = _string_dict(node.get("fields"), "schema fields")
                if any(
                    not isinstance(field, dict)
                    or cast(dict[str, Any], field).get("type") != "model-field"
                    or not isinstance(cast(dict[str, Any], field).get("schema"), dict)
                    for field in model_fields.values()
                ):
                    raise _incompatible("schema fields contain incompatible model-field entries")
            for key, child in node.items():
                # Metadata contains user JSON Schema examples, not validator
                # nodes; serializer schemas have a different wrapper contract.
                if key not in ("metadata", "serialization"):
                    check(child)
        elif isinstance(node, (list, tuple)):
            for child in cast(list[Any] | tuple[Any, ...], node):
                check(child)

    check(schema)
    return cast(CoreSchema, schema)


def core_schema(cls: type[BaseModel]) -> CoreSchema:
    return _checked_schema(getattr(cls, "__pydantic_core_schema__", None))


def compile_validator(schema: object) -> SchemaValidator:
    try:
        return SchemaValidator(_checked_schema(schema))
    except (TypeError, ValueError) as exc:
        raise _incompatible("validator schema could not be compiled") from exc


def validator(cls: type[BaseModel]) -> SchemaValidator:
    result = getattr(cls, "__pydantic_validator__", None)
    if not isinstance(result, SchemaValidator):
        raise _incompatible("model validator has an incompatible shape")
    return result


def is_complete(cls: type[BaseModel]) -> bool:
    complete = getattr(cls, "__pydantic_complete__", None)
    if not isinstance(complete, bool):
        raise _incompatible("model completion flag must be a boolean")
    return complete


def _rewrite(
    value: Any, *, canonical: bool, by_alias: bool | None = None, by_name: bool | None = None
) -> Any:
    if isinstance(value, dict):
        value = cast(dict[str, Any], value)
        result: dict[str, Any] = {
            key: child
            if key in ("metadata", "serialization")
            else _rewrite(child, canonical=canonical, by_alias=by_alias, by_name=by_name)
            for key, child in value.items()
            if not (canonical and value.get("type") == "model-field" and key == "validation_alias")
        }
        if value.get("type") == "model":
            settings = dict(result.get("config", {}))
            if canonical:
                settings.update(validate_by_name=True, validate_by_alias=False)
            else:
                if by_alias is not None:
                    settings["validate_by_alias"] = by_alias
                if by_name is not None:
                    settings["validate_by_name"] = by_name
            result["config"] = settings
        return result
    if isinstance(value, list):
        return [
            _rewrite(child, canonical=canonical, by_alias=by_alias, by_name=by_name)
            for child in cast(list[Any], value)
        ]
    if isinstance(value, tuple):
        return tuple(
            _rewrite(child, canonical=canonical, by_alias=by_alias, by_name=by_name)
            for child in cast(tuple[Any, ...], value)
        )
    return value


def invalidate_validators(cls: type[BaseModel]) -> None:
    # Class-local storage avoids a global cache retaining generated model classes.
    for name in ("_pd_canonical_validator", "_pd_alias_validators"):
        setattr(cls, name, None)


def canonical_validator(cls: type[BaseModel]) -> SchemaValidator:
    schema = core_schema(cls)
    cache = cls.__dict__.get("_pd_canonical_validator")
    if cache is None or cache[0] is not schema:
        cache = (schema, compile_validator(_rewrite(schema, canonical=True)))
        setattr(cls, "_pd_canonical_validator", cache)
    return cast(SchemaValidator, cache[1])


def entry_validator(
    cls: type[BaseModel], by_alias: bool | None, by_name: bool | None
) -> SchemaValidator:
    if by_alias is None and by_name is None:
        return validator(cls)
    schema = core_schema(cls)
    cache: Any = cls.__dict__.get("_pd_alias_validators")
    if cache is None or cache[0] is not schema:
        cache = (schema, {})
        setattr(cls, "_pd_alias_validators", cache)
    variants = cache[1]
    key = (by_alias, by_name)
    if key not in variants:
        variants[key] = compile_validator(
            _rewrite(schema, canonical=False, by_alias=by_alias, by_name=by_name)
        )
    return cast(SchemaValidator, variants[key])


def wrap_model_schema(
    source: type[BaseModel],
    handler: GetCoreSchemaHandler,
    finish: Callable[[object, Callable[[object], BaseModel], object], BaseModel],
    snapshot: Callable[[BaseModel], object],
) -> CoreSchema:
    schema: dict[str, Any] = dict(_checked_schema(handler(source)))
    ref = schema.pop("ref", None)
    if ref is not None and not isinstance(ref, str):
        raise _incompatible("model schema reference must be a string")

    def validate(value: Any, next_validator: Any, info: Any) -> Any:
        def next_model(input_value: object) -> BaseModel:
            result = next_validator(input_value)
            if not isinstance(result, BaseModel):
                raise _incompatible("model validator returned an incompatible value")
            return result

        return finish(value, next_model, info.context)

    def serialize(value: Any, next_serializer: Any, info: Any) -> Any:
        if not isinstance(value, BaseModel):
            raise _incompatible("model serializer received an incompatible value")
        return next_serializer(snapshot(value))

    return schema_tools.with_info_wrap_validator_function(
        validate,
        cast(CoreSchema, schema),
        ref=ref,
        serialization=schema_tools.wrap_serializer_function_ser_schema(serialize, info_arg=True),
    )


def raw_set(target: object, name: str, value: object) -> None:
    object.__setattr__(target, name, value)


def slot_value(target: object, name: str, missing: object) -> object:
    try:
        return object.__getattribute__(target, name)
    except AttributeError:
        return missing


def restore_slot(target: object, name: str, value: object, missing: object) -> None:
    if value is missing:
        try:
            object.__delattr__(target, name)
        except AttributeError:
            pass
    else:
        raw_set(target, name, value)


def storage_updates(
    model: BaseModel, data: dict[str, object], explicit: set[str]
) -> list[SlotUpdate]:
    field_map = fields(type(model))
    return [
        (model, "__dict__", {k: v for k, v in data.items() if k in field_map}),
        (
            model,
            "__pydantic_extra__",
            {k: v for k, v in data.items() if k not in field_map}
            if config(type(model)).get("extra") == "allow"
            else None,
        ),
        (model, "__pydantic_fields_set__", set(explicit)),
    ]


def replace_storage(model: BaseModel, data: dict[str, object], explicit: set[str]) -> None:
    for target, name, value in storage_updates(model, data, explicit):
        raw_set(target, name, value)


def blank_model(cls: type[M], data: dict[str, object], explicit: set[str]) -> M:
    obj = object.__new__(cls)
    replace_storage(obj, data, explicit)
    raw_set(obj, "__pydantic_private__", None)
    return obj


def generic_parameters(cls: type[BaseModel]) -> bool:
    metadata = _string_dict(
        getattr(cls, "__pydantic_generic_metadata__", None), "generic model metadata"
    )
    parameters = metadata.get("parameters")
    if not isinstance(parameters, tuple):
        raise _incompatible("generic model parameters must be a tuple")
    return bool(cast(tuple[object, ...], parameters))


def extra_value_annotation(cls: type[BaseModel]) -> object | None:
    """Read completed extra metadata, including inherited/generic substitutions."""
    from typing import Annotated, get_args, get_origin

    try:
        from pydantic._internal._fields import PydanticExtraInfo
        from pydantic._internal._generics import get_model_typevars_map, replace_types
    except ImportError as exc:
        raise _incompatible("extra annotation metadata API is unavailable") from exc
    info = getattr(cls, "__pydantic_extra_info__", None)
    if info is None:
        return None
    if not isinstance(info, PydanticExtraInfo):
        raise _incompatible("extra annotation metadata has an incompatible shape")
    complete: object = getattr(info, "complete", None)
    if not isinstance(complete, bool):
        raise _incompatible("extra annotation completion flag must be a boolean")
    if not complete or info.annotation is None:
        return None
    annotation = replace_types(info.annotation, get_model_typevars_map(cls))
    while get_origin(annotation) is Annotated:
        annotation = get_args(annotation)[0]
    args = get_args(annotation)
    if get_origin(annotation) is not dict or len(args) != 2:
        raise _incompatible("completed extra annotation must be dict[str, V]")
    return args[1]


ensure_supported()
