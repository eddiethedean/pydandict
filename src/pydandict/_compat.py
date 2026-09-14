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


def _native_model_schema(node: dict[str, Any]) -> dict[str, Any]:
    if node.get("metadata", {}).get("pydandict_entry_boundary"):
        result = dict(node["schema"]["json_schema"])
        if "ref" in node:
            result["ref"] = node["ref"]
        return result
    return node


def _identity(value: Any) -> Any:
    return value


def _isolated_callback(function: Any, detach: Callable[[object], object], *, after: bool) -> Any:
    def isolated(value: Any, *args: Any) -> Any:
        # After-model callbacks receive a newly allocated model, whose fields
        # were detached at the model-fields boundary. Preserve its identity.
        candidate = value if after and isinstance(value, BaseModel) else detach(value)
        return function(candidate, *args)

    return isolated


def _native_schema(value: Any, detach: Callable[[object], object]) -> Any:
    """Keep native input until validation; isolate only existing callback inputs.

    A root before/wrap/chain callback changes JSON/StringInput to Python input.
    Existing user callbacks already perform that conversion, so cloning inside
    their callable preserves the original schema's coercion and option semantics.
    Detach validated fields/extras before model allocation and after callbacks.
    """
    if isinstance(value, dict):
        node = cast(dict[str, Any], value)
        node = _native_model_schema(node)
        if node.get("metadata", {}).get("pydandict_native_boundary"):
            return node  # A nested DictModel already owns this boundary.
        result: dict[str, Any] = {
            key: child if key in ("metadata", "serialization") else _native_schema(child, detach)
            for key, child in node.items()
        }
        kind = node.get("type")
        if kind in ("function-before", "function-wrap", "function-after", "function-plain"):
            function = dict(result["function"])
            function["function"] = _isolated_callback(
                function["function"], detach, after=kind == "function-after"
            )
            result["function"] = function
            result["metadata"] = {
                **result.get("metadata", {}),
                "pydandict_original_function": node["function"],
            }
        if kind == "model-fields":
            return schema_tools.no_info_after_validator_function(
                detach, cast(CoreSchema, result), metadata={"pydandict_detached_fields": True}
            )
        if kind == "model-field":
            field_schema = result["schema"]
            # ModelFields detects required/default status from the outer node.
            # Keep defaults outermost while detaching before the next factory.
            if field_schema.get("type") == "default":
                field_schema = dict(field_schema)
                field_schema["schema"] = schema_tools.no_info_after_validator_function(
                    detach, field_schema["schema"], metadata={"pydandict_detached_fields": True}
                )
                result["schema"] = field_schema
            else:
                result["schema"] = schema_tools.no_info_after_validator_function(
                    detach, field_schema, metadata={"pydandict_detached_fields": True}
                )
        return result
    if isinstance(value, list):
        return [_native_schema(child, detach) for child in cast(list[Any], value)]
    if isinstance(value, tuple):
        return tuple(_native_schema(child, detach) for child in cast(tuple[Any, ...], value))
    return value


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
                    while inner.get("type") in (
                        "function-before",
                        "function-after",
                        "function-wrap",
                    ):
                        inner = _string_dict(inner.get("schema"), "incomplete model inner schema")
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
    for name in ("_pd_canonical_validator", "_pd_alias_validators", "_pd_python_validators"):
        setattr(cls, name, None)


def canonical_validator(cls: type[BaseModel]) -> SchemaValidator:
    schema = core_schema(cls)
    cache = cls.__dict__.get("_pd_canonical_validator")
    if cache is None or cache[0] is not schema:
        cache = (schema, compile_validator(_rewrite(_python_schema(schema), canonical=True)))
        setattr(cls, "_pd_canonical_validator", cache)
    return cast(SchemaValidator, cache[1])


def _python_schema(value: Any) -> Any:
    """Select isolated Python validation without changing native public schemas."""
    if isinstance(value, dict):
        node = cast(dict[str, Any], value)
        metadata = node.get("metadata", {})
        if metadata.get("pydandict_entry_boundary"):
            result = _python_schema(node["schema"]["json_schema"])
            if "ref" in node:
                result["ref"] = node["ref"]
            return result
        if metadata.get("pydandict_detached_fields"):
            return _python_schema(node["schema"])
        result = {
            key: child if key in ("metadata", "serialization") else _python_schema(child)
            for key, child in node.items()
        }
        if metadata.get("pydandict_native_boundary"):
            result["type"] = "function-wrap"
            result["function"] = {
                "type": "with-info",
                "function": metadata["pydandict_python_function"],
            }
        elif "pydandict_original_function" in metadata:
            result["function"] = metadata["pydandict_original_function"]
        return result
    if isinstance(value, list):
        return [_python_schema(child) for child in cast(list[Any], value)]
    if isinstance(value, tuple):
        return tuple(_python_schema(child) for child in cast(tuple[Any, ...], value))
    return value


def python_entry_validator(
    cls: type[BaseModel], by_alias: bool | None, by_name: bool | None
) -> SchemaValidator:
    schema = core_schema(cls)
    cache: Any = cls.__dict__.get("_pd_python_validators")
    if cache is None or cache[0] is not schema:
        cache = (schema, {})
        setattr(cls, "_pd_python_validators", cache)
    variants = cache[1]
    key = (by_alias, by_name)
    if key not in variants:
        variants[key] = compile_validator(
            _rewrite(_python_schema(schema), canonical=False, by_alias=by_alias, by_name=by_name)
        )
    return cast(SchemaValidator, variants[key])


def entry_validator(
    cls: type[BaseModel], by_alias: bool | None, by_name: bool | None
) -> SchemaValidator:
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
    native_finish: Callable[[BaseModel, CoreSchema, dict[str, object]], BaseModel],
    detach: Callable[[object], object],
) -> CoreSchema:
    namespace = schema_namespace(handler)
    schema: dict[str, Any] = dict(_checked_schema(handler(source)))
    # Embedded schemas must remain model-shaped for discriminator inference.
    # Their containing DictModel's Python branch reconstructs the isolated
    # wrappers recursively; JSON/strings retain these native model boundaries.
    schema = _native_model_schema(schema)
    if schema.get("metadata", {}).get("pydandict_native_boundary"):
        return cast(CoreSchema, schema)
    ref = schema.pop("ref", None)
    if ref is not None and not isinstance(ref, str):
        raise _incompatible("model schema reference must be a string")

    def validate(value: Any, next_validator: Any, info: Any) -> Any:
        def next_model(input_value: object) -> BaseModel:
            result = next_validator(input_value)
            if not isinstance(result, BaseModel):
                raise _incompatible("model validator returned an incompatible value")
            return result

        return finish(value, next_model, info.context, cast(CoreSchema, schema), namespace)

    def finish_native(value: Any) -> BaseModel:
        if not isinstance(value, BaseModel):
            raise _incompatible("model validator returned an incompatible value")
        return native_finish(value, cast(CoreSchema, schema), namespace)

    def serialize(value: Any, next_serializer: Any, info: Any) -> Any:
        if not isinstance(value, BaseModel):
            raise _incompatible("model serializer received an incompatible value")
        return next_serializer(snapshot(value))

    # The public schema remains model-shaped for Pydantic's discriminated-union
    # inference. No root callback runs until native input has been validated.
    native = schema_tools.no_info_after_validator_function(
        finish_native,
        cast(CoreSchema, _native_schema(schema, detach)),
        metadata={"pydandict_native_boundary": True, "pydandict_python_function": validate},
        serialization=schema_tools.wrap_serializer_function_ser_schema(serialize, info_arg=True),
    )
    python = schema_tools.no_info_before_validator_function(detach, native)
    return schema_tools.no_info_after_validator_function(
        _identity,
        schema_tools.json_or_python_schema(native, cast(CoreSchema, python)),
        ref=ref,
        metadata={"pydandict_entry_boundary": True},
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
