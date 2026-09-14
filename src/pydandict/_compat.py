"""The checked, version-sensitive Pydantic storage and schema boundary."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, TypeVar, cast

import pydantic
from pydantic import BaseModel, ConfigDict, GetCoreSchemaHandler
from pydantic.config import ExtraValues
from pydantic.fields import FieldInfo
from pydantic_core import CoreSchema, SchemaValidator, ValidationError
from pydantic_core import core_schema as schema_tools

SUPPORTED_PYDANTIC_VERSION = "2.13.4"
M = TypeVar("M", bound=BaseModel)
SlotUpdate = tuple[object, str, object]
EntryOptions = tuple[bool | None, bool | None, bool | None, ExtraValues | None, object]
_ENTRY_OPTIONS: ContextVar[EntryOptions | None] = ContextVar(
    "pydandict_entry_options", default=None
)


@contextmanager
def entry_options(
    by_alias: bool | None,
    by_name: bool | None,
    strict: bool | None,
    extra: ExtraValues | None,
    context: object,
):
    token = _ENTRY_OPTIONS.set((by_alias, by_name, strict, extra, context))
    try:
        yield
    finally:
        _ENTRY_OPTIONS.reset(token)


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


def schema_namespace(handler: GetCoreSchemaHandler) -> dict[str, object]:
    """Return the annotation namespace used for this schema generation."""
    generator = getattr(handler, "_generate_schema", None)
    namespace = getattr(generator, "_types_namespace", None)
    if namespace is None:
        raise _incompatible("schema generator namespace is unavailable")
    result: dict[str, object] = {}
    for name in ("globals", "locals"):
        values = getattr(namespace, name, None)
        if not isinstance(values, Mapping):
            raise _incompatible("schema generator namespace has an incompatible shape")
        typed_values = cast(Mapping[str, object], values)
        result.update({key: typed_values[key] for key in typed_values})
    return result


def audit_incomplete_model(
    schema: object,
    callback: Callable[[type[BaseModel], str], None],
) -> None:
    """Report mutable schema fields for the incomplete model in a generated schema.

    Core-schema node shapes are intentionally interpreted here, at the adapter
    boundary. The callback receives only model and field names; declaration-aware
    policy remains in the core module.
    """
    root = _checked_schema(schema)

    def contains_mutable(node: object, seen: set[int] | None = None) -> bool:
        if seen is None:
            seen = set()
        if not isinstance(node, (dict, list, tuple)):
            return False
        identity = id(cast(object, node))
        if identity in seen:
            return False
        seen.add(identity)
        if isinstance(node, dict):
            node_map = cast(dict[str, object], node)
            if node_map.get("type") in {"list", "dict", "set"}:
                return True
            return any(
                contains_mutable(value, seen)
                for key, value in node_map.items()
                if key not in ("metadata", "serialization")
            )
        return any(
            contains_mutable(value, seen) for value in cast(list[object] | tuple[object, ...], node)
        )

    def walk(node: object, seen: set[int] | None = None) -> None:
        if seen is None:
            seen = set()
        if not isinstance(node, (dict, list, tuple)):
            return
        identity = id(cast(object, node))
        if identity in seen:
            return
        seen.add(identity)
        if isinstance(node, dict):
            node_map = cast(dict[str, object], node)
            if node_map.get("type") == "model":
                model = node_map.get("cls")
                if (
                    isinstance(model, type)
                    and issubclass(model, BaseModel)
                    and not is_complete(model)
                ):
                    inner = _string_dict(node_map.get("schema"), "incomplete model schema")
                    fields_map = _string_dict(inner.get("fields", {}), "incomplete model fields")
                    for field_name, field_node in fields_map.items():
                        field_map = _string_dict(field_node, "incomplete model field")
                        if contains_mutable(field_map.get("schema")):
                            callback(model, field_name)
                    if contains_mutable(inner.get("extras_schema")):
                        callback(model, "__pydantic_extra__")
                # Continue through nested model nodes: an incomplete child can
                # retain unresolved Python annotations while its parent schema
                # was compiled with the active caller namespace.
            for key, value in node_map.items():
                if key not in ("metadata", "serialization"):
                    walk(value, seen)
        else:
            for value in cast(list[object] | tuple[object, ...], node):
                walk(value, seen)

    walk(root)


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
    finish: Callable[
        [object, Callable[[object], BaseModel], object, CoreSchema, dict[str, object]], BaseModel
    ],
    snapshot: Callable[[BaseModel], object],
) -> CoreSchema:
    namespace = schema_namespace(handler)
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

        # DictModel's public class methods make their entry options available
        # here.  TypeAdapter enters this schema directly, however, and
        # ValidationInfo deliberately exposes neither strict nor extra.  Start
        # with the original handler in that path: pydantic keeps its dynamic
        # strict/extra policies there.  Its handler is Python-mode, so only
        # replay the small set of strict JSON/string scalar representations
        # that Pydantic accepts in their native mode but rejects in Python mode.
        options = _ENTRY_OPTIONS.get()
        if options is None:

            def type_adapter_model(input_value: object) -> BaseModel:
                try:
                    return next_model(input_value)
                except ValidationError as error:
                    replayable = {
                        "bytes_type",
                        "date_type",
                        "datetime_type",
                        "time_type",
                        "time_delta_type",
                        "is_instance_of",
                    }
                    errors = error.errors()
                    if (
                        info.mode not in ("json", "string")
                        or not errors
                        or not all(
                            item.get("type") in replayable | {"extra_forbidden"} for item in errors
                        )
                    ):
                        raise
                    mode_validator = SchemaValidator(cast(CoreSchema, schema))
                    if info.mode == "json":
                        parsed = mode_validator.validate_json(
                            json.dumps(input_value),
                            strict=True,
                            extra="allow",
                            context=info.context,
                        )
                    else:
                        parsed = mode_validator.validate_strings(
                            cast(Any, input_value), strict=True, extra="allow", context=info.context
                        )
                    # Feed the native-mode scalar representation back through
                    # the original handler so TypeAdapter's dynamic extra
                    # policy is still enforced there.
                    return next_model(parsed)

            return finish(
                value, type_adapter_model, info.context, cast(CoreSchema, schema), namespace
            )

        # A wrap validator's ``next_validator`` is a Python-mode handler even
        # when the outer SchemaValidator was entered through validate_json or
        # validate_strings. Re-run the unwrapped model schema in that mode, but
        # do so through ``finish``: it detaches caller input before user
        # validators run. The class-method boundary supplies its applicable
        # strict, extra, alias and context options above.
        by_alias, by_name, strict, extra, context = options
        mode_schema = _rewrite(
            schema,
            canonical=False,
            by_alias=by_alias,
            by_name=by_name,
        )
        if info.mode == "string":
            mode_validator = SchemaValidator(cast(CoreSchema, mode_schema))
            return finish(
                value,
                lambda input_value: cast(
                    BaseModel,
                    mode_validator.validate_strings(
                        cast(Any, input_value), strict=strict, extra=extra, context=context
                    ),
                ),
                info.context,
                cast(CoreSchema, schema),
                namespace,
            )
        if info.mode == "json":
            mode_validator = SchemaValidator(cast(CoreSchema, mode_schema))
            return finish(
                value,
                lambda input_value: cast(
                    BaseModel,
                    mode_validator.validate_json(
                        json.dumps(input_value), strict=strict, extra=extra, context=context
                    ),
                ),
                info.context,
                cast(CoreSchema, schema),
                namespace,
            )
        return finish(value, next_model, info.context, cast(CoreSchema, schema), namespace)

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
