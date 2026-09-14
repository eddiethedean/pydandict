"""PydanDict model/mapping implementation with isolated ownership transactions.

Version-sensitive Pydantic operations live in the checked compatibility adapter.
Ownership uses pointer-swap commits and raw-state snapshots.
"""

from __future__ import annotations

import sys
from collections.abc import Collection, Iterable, Iterator, Mapping, MutableMapping
from contextvars import ContextVar
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from typing import (
    Any,
    Callable,
    ClassVar,
    LiteralString,
    Protocol,
    Self,
    SupportsIndex,
    TypeVar,
    cast,
    overload,
)
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    GetCoreSchemaHandler,
    PydanticUserError,
    ValidationError,
)
from pydantic.config import ExtraValues
from pydantic_core import CoreSchema, PydanticCustomError

from . import _compat
from ._containers import Owned, OwnedDict, OwnedList, OwnedSet, P, Path, R, RootCoordinator

M = TypeVar("M", bound="DictModel")


_BUILDING: ContextVar[bool] = ContextVar("pydandict_building", default=False)
_CANONICAL: ContextVar[bool] = ContextVar("pydandict_canonical", default=False)
_DEFERRED_NAMESPACE: ContextVar[dict[str, object] | None] = ContextVar(
    "pydandict_deferred_namespace", default=None
)
_MISSING = object()
_IMMUTABLE = {
    type(None),
    bool,
    int,
    float,
    str,
    bytes,
    Decimal,
    date,
    datetime,
    time,
    timedelta,
    UUID,
}


def _root(value: object) -> DictModel | None:
    try:
        root: object = object.__getattribute__(value, "_pd_root")
    except AttributeError:
        return None
    if root is None or isinstance(root, DictModel):
        return root
    raise TypeError("pydandict_internal_state: root must be a DictModel")


def _model_path(model: DictModel) -> Path:
    value = _compat.slot_value(model, "_pd_path", ())
    if not isinstance(value, tuple):
        raise TypeError("pydandict_internal_path: model path must be a tuple")
    return cast(Path, value)


def _busy(model: DictModel) -> bool:
    value = _compat.slot_value(model, "_pd_busy", False)
    if not isinstance(value, bool):
        raise TypeError("pydandict_internal_state: busy marker must be a boolean")
    return value


def _version(target: object, name: str) -> int:
    value = _compat.slot_value(target, name, 0)
    if not isinstance(value, int):
        raise TypeError("pydandict_internal_state: version must be an integer")
    return value


def _data(model: DictModel) -> dict[str, object]:
    fields = _compat.fields(type(model))
    storage = _compat.raw_state(model)
    data: dict[str, object] = {k: v for k, v in storage.items() if k in fields}
    extra = _compat.raw_extra(model)
    data.update(extra or {})
    return data


def _extra_storage(model: DictModel) -> dict[str, object]:
    extra = _compat.raw_extra(model)
    if extra is None:
        raise TypeError("pydandict_incompatible_pydantic: expected extra storage")
    return extra


def _blank(cls: type[M], data: dict[str, object], fields_set: set[str]) -> M:
    # Internal trusted snapshot only; never exposed until validated/owned.
    return _compat.blank_model(cls, data, fields_set)


@overload
def _clone(
    value: M,
    origins: dict[int, object] | None = None,
    active: set[int] | None = None,
    *,
    hash_position: bool = False,
) -> M: ...
@overload
def _clone(
    value: object,
    origins: dict[int, object] | None = None,
    active: set[int] | None = None,
    *,
    hash_position: bool = False,
) -> object: ...


def _clone(
    value: object,
    origins: dict[int, object] | None = None,
    active: set[int] | None = None,
    *,
    hash_position: bool = False,
) -> object:
    if type(value) in _IMMUTABLE:
        if type(value) in (datetime, time):
            zone = cast(datetime | time, value).tzinfo
            if zone is not None and type(zone) is not timezone:
                raise TypeError(
                    "pydandict_unsupported_value: custom timezone values are unsupported"
                )
        return value
    if active is None:
        active = set()
    identity = id(value)
    if hash_position and (
        isinstance(value, (DictModel, Owned)) or type(value) in (list, dict, set)
    ):
        raise TypeError(
            "pydandict_unsupported_value: mutable containers, DictModels and guards "
            "are not safe hash members"
        )
    if identity in active:
        raise TypeError("pydandict_cycle: cyclic values are unsupported")
    active.add(identity)
    try:
        if isinstance(value, DictModel):
            value._ensure_alive()  # pyright: ignore[reportPrivateUsage]
            result = _blank(
                type(value),
                {k: _clone(v, origins, active) for k, v in _data(value).items()},
                _compat.fields_set(value),
            )
        elif type(value) in (list, OwnedList):
            result = [
                _clone(v, origins, active, hash_position=hash_position)
                for v in cast(list[object], value)
            ]
        elif type(value) in (dict, OwnedDict):
            mapping = cast(dict[object, object], value)
            result = {
                _clone(k, None, active, hash_position=True): _clone(
                    v, origins, active, hash_position=hash_position
                )
                for k, v in mapping.items()
            }
        elif type(value) in (set, OwnedSet):
            result = {_clone(v, None, active, hash_position=True) for v in cast(set[object], value)}
        elif type(value) is tuple:
            result = tuple(
                _clone(v, origins, active, hash_position=hash_position)
                for v in cast(tuple[object, ...], value)
            )
        elif type(value) is frozenset:
            result = frozenset(
                _clone(v, None, active, hash_position=True) for v in cast(frozenset[object], value)
            )
        else:
            raise TypeError(f"pydandict_unsupported_value: {type(value).__name__}")
        if origins is not None and (
            isinstance(value, Owned) or _root(cast(object, value)) is not None
        ):
            origins[id(result)] = value
        return result
    finally:
        active.remove(identity)


def _fingerprint(value: object) -> object:
    # No user-defined equality/hash methods are called. The envelope is closed.
    if isinstance(value, DictModel):
        return (
            type(value),
            tuple((k, _fingerprint(v)) for k, v in _data(value).items()),
        )
    if isinstance(value, (list, tuple, OwnedList)):
        return ("sequence", tuple(_fingerprint(v) for v in cast(Iterable[object], value)))
    if isinstance(value, (dict, OwnedDict)):
        return (
            "dict",
            tuple(
                (_fingerprint(k), _fingerprint(v))
                for k, v in cast(Mapping[object, object], value).items()
            ),
        )
    if isinstance(value, (set, frozenset, OwnedSet)):
        return ("set", frozenset(_fingerprint(v) for v in cast(Iterable[object], value)))
    if type(value) not in _IMMUTABLE:
        raise TypeError(f"pydandict_unsupported_value: {type(value).__name__}")
    # repr handles NaN without an unequal-to-itself drift check.
    return (type(value), repr(value))


def _at(value: object, path: Path) -> object:
    for part in path:
        value = _child(value, part)
    return value


def _child(value: object, part: object) -> object:
    if isinstance(value, DictModel):
        if not isinstance(part, str):
            raise TypeError("pydandict_internal_path: model path must use a string")
        return _data(value)[part]
    if isinstance(value, (dict, OwnedDict)):
        return cast(Mapping[object, object], value)[part]
    if isinstance(value, (list, tuple, OwnedList)) and isinstance(part, int):
        return cast(list[object] | tuple[object, ...] | OwnedList[object], value)[part]
    raise TypeError("pydandict_internal_path: path does not address a container")


def _policy(model: DictModel, code: LiteralString, key: str | int, message: LiteralString) -> None:
    raise ValidationError.from_exception_data(
        type(model).__name__,
        [
            {
                "type": PydanticCustomError(code, message),
                "loc": (key,),
                "input": None,
            }
        ],
    )


def _annotation_error(field: str, annotation: object, replacement: str | None = None) -> None:
    detail = f"field {field!r} uses unsupported annotation {annotation!r}"
    if replacement is not None:
        detail += f"; use {replacement}"
    raise TypeError(f"pydandict_unsupported_annotation: {detail}")


def _check_annotation(
    annotation: object,
    field: str,
    *,
    nested: bool = False,
    reject_generic: bool = False,
    seen: set[int] | None = None,
) -> None:
    """Reject mutable concrete annotations before a model instance can escape."""
    from collections.abc import MutableMapping as ABCMapping
    from collections.abc import MutableSequence as ABCSequence
    from collections.abc import MutableSet as ABCSet
    from types import UnionType
    from typing import Annotated, TypeVar, Union, get_args, get_origin

    from typing_extensions import TypeAliasType

    if seen is None:
        seen = set()
    identity = id(annotation)
    if identity in seen:
        return
    seen.add(identity)

    if isinstance(annotation, TypeAliasType):
        _check_annotation(
            annotation.__value__,
            field,
            nested=nested,
            reject_generic=reject_generic,
            seen=seen,
        )
        return

    if annotation is Any or annotation is object or isinstance(annotation, TypeVar):
        return
    origin = get_origin(annotation)
    if origin is Annotated:
        args = get_args(annotation)
        if args:
            _check_annotation(
                args[0], field, nested=nested, reject_generic=reject_generic, seen=seen
            )
        return
    if origin in (list,):
        _annotation_error(field, annotation, "collections.abc.MutableSequence")
    if origin in (dict,):
        _annotation_error(field, annotation, "collections.abc.MutableMapping")
    if origin in (set,):
        _annotation_error(field, annotation, "collections.abc.MutableSet")
    if isinstance(annotation, type) and annotation in (list, dict, set):
        replacement = {
            list: "collections.abc.MutableSequence",
            dict: "collections.abc.MutableMapping",
            set: "collections.abc.MutableSet",
        }[annotation]
        _annotation_error(field, annotation, replacement)
    if origin in (Union, UnionType):
        for arg in get_args(annotation):
            if arg is type(None):
                continue
            _check_annotation(arg, field, nested=True, reject_generic=reject_generic, seen=seen)
        return
    if origin in (tuple, frozenset, ABCSequence, ABCMapping, ABCSet):
        for arg in get_args(annotation):
            _check_annotation(arg, field, nested=True, reject_generic=reject_generic, seen=seen)
        return
    if isinstance(annotation, type) and annotation in (ABCSequence, ABCMapping, ABCSet):
        return
    # Nested model classes are safe only when they use this ownership contract.
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        if not issubclass(annotation, DictModel):
            _annotation_error(field, annotation)
        if reject_generic and _compat.generic_parameters(annotation):
            raise TypeError(
                "pydandict_unsupported_annotation: generic DictModel instances "
                "must be explicitly specialized"
            )
        return
    # Pydantic's unresolved forward references are checked when model_rebuild
    # resolves them; arbitrary custom values are rejected by _clone at runtime.


def _check_extra_annotation(cls: type[DictModel], *, reject_generic: bool = False) -> None:
    annotation = _compat.extra_value_annotation(cls)
    if annotation is not None:
        _check_annotation(annotation, "__pydantic_extra__", reject_generic=reject_generic)


def _audit_incomplete_field(
    model: type[BaseModel], field_name: str, namespace: dict[str, object]
) -> None:
    """Check one deferred declaration using Pydantic's active type namespace.

    Resolving the complete model at once is too coarse: an unrelated unresolved
    ``ClassVar`` (which is intentionally outside our stored-field policy) must
    not prevent a deferred stored field from being audited.
    """
    import typing

    resolution_namespace: dict[str, object] = {name: value for name, value in vars(typing).items()}
    module = sys.modules.get(model.__module__)
    if module is not None:
        resolution_namespace.update(vars(module))
    resolution_namespace.update(namespace)

    raw_annotations = cast(object, getattr(model, "__annotations__", {}))
    annotation: object = object
    if isinstance(raw_annotations, dict):
        annotation = cast(dict[str, object], raw_annotations).get(field_name, object)
    if annotation is object:
        field = _compat.fields(model).get(field_name)
        annotation = cast(object, field.annotation) if field is not None else object

    # Use get_type_hints on a single synthetic return annotation. This keeps
    # resolution local to the field and therefore tolerates unrelated unresolved
    # annotations on the model while retaining support for nested aliases.
    def deferred_annotation() -> object:
        return object()

    deferred_annotation.__annotations__["return"] = annotation
    try:
        annotation = typing.get_type_hints(
            deferred_annotation,
            globalns=resolution_namespace,
            localns=resolution_namespace,
            include_extras=True,
        ).get("return", annotation)
    except (NameError, TypeError):
        pass
    if field_name == "__pydantic_extra__":
        args = typing.get_args(annotation)
        if typing.get_origin(annotation) is dict and len(args) == 2:
            annotation = args[1]
    _check_annotation(annotation, field_name, reject_generic=True)


def _validate(candidate: M) -> M:
    token = _BUILDING.set(True)
    canonical_token = _CANONICAL.set(True)
    try:
        result: object = _compat.canonical_validator(type(candidate)).validate_python(candidate)
        if not isinstance(result, type(candidate)):
            raise TypeError("pydandict_incompatible_pydantic: validation changed model type")
        return result
    finally:
        _CANONICAL.reset(canonical_token)
        _BUILDING.reset(token)


def _walk(
    value: object, path: Path = ()
) -> Iterator[tuple[DictModel | Owned[Collection[object]], Path]]:
    if isinstance(value, (DictModel, Owned)):
        yield cast("DictModel | Owned[Collection[object]]", value), path
    if isinstance(value, DictModel):
        for key, child in _data(value).items():
            yield from _walk(child, path + (key,))
    elif isinstance(value, (list, tuple, OwnedList)):
        for key, child in enumerate(cast(Iterable[object], value)):
            yield from _walk(child, path + (key,))
    elif isinstance(value, (dict, OwnedDict)):
        for key, child in cast(Mapping[object, object], value).items():
            yield from _walk(child, path + (key,))


def _prepare(
    root: DictModel,
    expected: object,
    validated: object,
    origins: dict[int, object],
    changed: set[Path],
) -> list[_compat.SlotUpdate]:
    coordinator = root._ownership_coordinator()  # pyright: ignore[reportPrivateUsage] # Typed package collaborator.
    updates: list[tuple[object, str, object]] = []
    retained: set[int] = set()
    nodes: list[DictModel | Owned[Collection[object]]] = []

    def prepare(before: object, after: object, path: tuple[object, ...]) -> object:
        old = origins.get(id(before))
        descendant_change = any(p[: len(path)] == path for p in changed)
        affected = descendant_change or any(path[: len(p)] == p for p in changed)
        check_untouched = before is not _MISSING and (
            not affected or (old is not None and not descendant_change)
        )
        if check_untouched and _fingerprint(before) != _fingerprint(after):
            raise TypeError(
                "pydandict_canonical_drift: canonical revalidation changed "
                f"untouched state at {path!r}; "
                "use idempotent validators"
            )
        if isinstance(after, DictModel):
            if old is not None and type(old) is not type(after):
                old = None
            target = old if isinstance(old, DictModel) else _blank(type(after), {}, set())
            before_data = _data(before) if isinstance(before, DictModel) else {}
            after_data = _data(after)
            type(after)._check_names(after_data)  # pyright: ignore[reportPrivateUsage]
            model_values: dict[str, object] = {
                k: prepare(before_data.get(k, _MISSING), v, path + (k,))
                for k, v in after_data.items()
            }
            previous_keys = tuple(_data(target))
            updates.extend(_compat.storage_updates(target, model_values, after.model_fields_set))
            updates.extend(
                [
                    (target, "_pd_root", root),
                    (target, "_pd_alive", True),
                    (target, "_pd_path", path),
                    (
                        target,
                        "_pd_version",
                        _version(target, "_pd_version") + (tuple(model_values) != previous_keys),
                    ),
                ]
            )
        elif type(after) in (list, dict, set):
            cls: type[Owned[Collection[object]]]
            if isinstance(after, list):
                cls = cast(type[Owned[Collection[object]]], OwnedList)
            elif isinstance(after, dict):
                cls = cast(type[Owned[Collection[object]]], OwnedDict)
            else:
                cls = cast(type[Owned[Collection[object]]], OwnedSet)
            if old is not None and type(old) is not cls:
                old = None
            target = old if isinstance(old, Owned) else cls()
            previous: list[object] | dict[object, object] | tuple[object, ...] = []
            values: list[object] | dict[object, object] | set[object]
            if isinstance(after, list):
                previous = cast(list[object], before) if isinstance(before, list) else []
                after_list = cast(list[object], after)
                if old is not None and len(previous) != len(after_list):
                    raise TypeError(
                        "pydandict_topology_change: validator changed owned list topology; "
                        "use topology-preserving validators"
                    )
                values = [
                    prepare(previous[i] if i < len(previous) else _MISSING, v, path + (i,))
                    for i, v in enumerate(after_list)
                ]
            elif isinstance(after, dict):
                previous = cast(dict[object, object], before) if isinstance(before, dict) else {}
                after_dict = cast(dict[object, object], after)
                if old is not None and tuple(previous) != tuple(after_dict):
                    raise TypeError(
                        "pydandict_topology_change: validator changed owned dictionary topology"
                    )
                values = {
                    _clone(k, hash_position=True): prepare(
                        previous.get(k, _MISSING), v, path + (k,)
                    )
                    for k, v in after_dict.items()
                }
            else:
                values = {_clone(v, hash_position=True) for v in cast(Iterable[object], after)}
            updates.extend(
                [
                    (target, "_data", values),
                    (target, "_root", coordinator),
                    (target, "_alive", True),
                    (target, "_path", path),
                    (target, "_version", _version(target, "_version") + 1),
                ]
            )
        elif type(after) is tuple:
            previous = cast(tuple[object, ...], before) if isinstance(before, tuple) else ()
            return tuple(
                prepare(previous[i] if i < len(previous) else _MISSING, v, path + (i,))
                for i, v in enumerate(cast(tuple[object, ...], after))
            )
        else:
            return _clone(after)
        if old is not None:
            retained.add(id(old))
        nodes.append(target)
        return target

    try:
        result = prepare(expected, validated, ())
    finally:
        # Release staged state on success and failure before the busy guard ends.
        for cell in prepare.__closure__ or ():
            if cell.cell_contents is prepare:
                cell.cell_contents = None
    assert result is root
    for node in cast(
        tuple[DictModel | Owned[Collection[object]], ...], _compat.slot_value(root, "_pd_nodes", ())
    ):
        if id(node) not in retained:
            updates.append((node, "_pd_alive" if isinstance(node, DictModel) else "_alive", False))
    updates.append((root, "_pd_nodes", tuple(nodes)))
    return updates


def _swap(target: object, name: str, value: object) -> None:
    _compat.raw_set(target, name, value)


def _commit(updates: list[tuple[object, str, object]]) -> None:
    # Hold old state through every swap; no owned payload is destroyed mid-commit.
    undo = [
        (target, name, _compat.slot_value(target, name, _MISSING)) for target, name, _ in updates
    ]
    try:
        for target, name, value in updates:
            _swap(target, name, value)
    except BaseException:
        for target, name, value in reversed(undo):
            _compat.restore_slot(target, name, value, _MISSING)
        raise


def _install(value: M) -> M:
    if _compat.raw_extra(value) and _compat.config(type(value)).get("extra") != "allow":
        raise TypeError(
            "pydandict_unsupported_configuration: construction extra override conflicts "
            "with ongoing class policy"
        )
    # Validate output ownership before anything escapes a constructor/framework.
    raw = _clone(value)
    _commit(_prepare(value, raw, raw, {id(raw): value}, {()}))
    object.__setattr__(value, "_pd_busy", False)
    return value


class _KeySource(Protocol):
    def keys(self) -> Iterable[str]: ...
    def __getitem__(self, key: str, /) -> object: ...


class DictModel(BaseModel, MutableMapping[str, object]):
    """Prototype model/mapping with isolated root transactions and owned trees."""

    __slots__ = (
        "_pd_root",
        "_pd_alive",
        "_pd_path",
        "_pd_version",
        "_pd_nodes",
        "_pd_busy",
    )
    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        validate_default=True,
        revalidate_instances="always",
    )
    _prototype_fault: ClassVar[Callable[[str], None] | None] = None

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[BaseModel], handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        def finish(
            value: object,
            next_validator: Callable[[object], BaseModel],
            context: object,
            schema: CoreSchema,
            namespace: dict[str, object],
        ) -> BaseModel:
            active_namespace = namespace or _DEFERRED_NAMESPACE.get() or {}
            namespace_token = _DEFERRED_NAMESPACE.set(active_namespace)
            try:
                if not _BUILDING.get() and _compat.generic_parameters(cls):
                    raise TypeError(
                        "pydandict_unsupported_annotation: generic DictModel instances "
                        "must be explicitly specialized"
                    )
                if not _BUILDING.get():
                    for field_name, field in cls.model_fields.items():
                        _check_annotation(field.annotation, field_name, reject_generic=True)
                    _check_extra_annotation(cls, reject_generic=True)
                if not _CANONICAL.get():
                    _compat.audit_incomplete_model(
                        schema,
                        lambda model, field_name: _audit_incomplete_field(
                            model, field_name, active_namespace
                        ),
                    )
                if _BUILDING.get():
                    if isinstance(value, DictModel):
                        if not _CANONICAL.get():
                            return _validate(value)
                        result = next_validator(_data(value))
                        _compat.set_fields_set(result, value.model_fields_set)
                        return result
                    return next_validator(value)
                if isinstance(value, DictModel):
                    # Existing models are public validation inputs, not writable
                    # validation targets. Clone the complete graph before invoking
                    # user validators so context and strictness apply to detached
                    # canonical Python data while the caller's root stays untouched.
                    detached = _clone(value)
                    validated = next_validator(_data(detached))
                    if not isinstance(validated, DictModel):
                        raise TypeError(
                            "pydandict_incompatible_pydantic: validation changed model type"
                        )
                    _compat.set_fields_set(validated, _compat.fields_set(detached))
                    return _install(validated)
                # Detach inputs before user validation, not only after construction.
                token = _BUILDING.set(True)
                try:
                    validated = next_validator(_clone(value))
                finally:
                    _BUILDING.reset(token)
                return _install(cast(DictModel, validated))
            finally:
                _DEFERRED_NAMESPACE.reset(namespace_token)

        def snapshot(value: BaseModel) -> object:
            model = cast(DictModel, value)
            model._ensure_alive()
            return _clone(model)

        return _compat.wrap_model_schema(source, handler, finish, snapshot)

    @classmethod
    def _entry_validator(
        cls, by_alias: bool | None, by_name: bool | None
    ) -> _compat.SchemaValidator:
        if by_alias is False and by_name is not True:
            raise PydanticUserError(
                "At least one of by_alias or by_name must be True",
                code="validate-by-alias-and-name-false",
            )
        if not _compat.is_complete(cls):
            # Entry -> public validation method -> caller, before adapter access
            # rejects Pydantic's legitimate deferred validator placeholder.
            cls.model_rebuild(_parent_namespace_depth=4)
        return _compat.entry_validator(cls, by_alias, by_name)

    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        extra: ExtraValues | None = None,
        from_attributes: bool | None = None,
        context: Any = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        with _compat.entry_options(by_alias, by_name):
            return cls._entry_validator(by_alias, by_name).validate_python(
                obj,
                strict=strict,
                extra=extra,
                from_attributes=from_attributes,
                context=context,
            )

    @classmethod
    def model_validate_json(
        cls,
        json_data: str | bytes | bytearray,
        *,
        strict: bool | None = None,
        extra: ExtraValues | None = None,
        context: Any = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        with _compat.entry_options(by_alias, by_name):
            return cls._entry_validator(by_alias, by_name).validate_json(
                json_data, strict=strict, extra=extra, context=context
            )

    @classmethod
    def model_validate_strings(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        extra: ExtraValues | None = None,
        context: Any = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        with _compat.entry_options(by_alias, by_name):
            return cls._entry_validator(by_alias, by_name).validate_strings(
                obj, strict=strict, extra=extra, context=context
            )

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: object) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        if not cls.model_config.get("validate_assignment") or not cls.model_config.get(
            "validate_default"
        ):
            raise TypeError("pydandict_unsupported_configuration: validation cannot be disabled")
        if cls.model_config.get("revalidate_instances") != "always":
            raise TypeError(
                "pydandict_unsupported_configuration: DictModel requires "
                "revalidate_instances='always'"
            )
        for field in cls.model_fields.values():
            if field.validate_default is False:
                raise TypeError(
                    "pydandict_unsupported_configuration: default validation cannot be disabled"
                )
        if cls.__private_attributes__:
            raise TypeError(
                "pydandict_unsupported_configuration: private attributes are not supported "
                "by DictModel"
            )
        if cls.model_post_init is not BaseModel.model_post_init:
            raise TypeError(
                "pydandict_unsupported_configuration: model_post_init is outside the "
                "supported hook contract"
            )
        if cls.__init__ is not BaseModel.__init__ or "__del__" in cls.__dict__:
            raise TypeError(
                "pydandict_unsupported_configuration: custom initialization/finalization"
            )
        if any(
            isinstance(value, property) and value.fset is not None
            for value in cls.__dict__.values()
        ):
            raise TypeError(
                "pydandict_unsupported_configuration: writable properties are outside "
                "the transaction API"
            )
        for name, field in cls.model_fields.items():
            _check_annotation(field.annotation, name)
        _check_extra_annotation(cls)
        cls._check_names(cls.model_fields)

    @classmethod
    def model_rebuild(
        cls,
        *,
        force: bool = False,
        raise_errors: bool = True,
        _parent_namespace_depth: int = 2,
        _types_namespace: Mapping[str, Any] | None = None,
    ) -> bool | None:
        # Preserve BaseModel's caller lookup across this additional wrapper frame.
        depth = _parent_namespace_depth + 1 if _parent_namespace_depth > 0 else 0
        rebuilt = super().model_rebuild(
            force=force,
            raise_errors=raise_errors,
            _parent_namespace_depth=depth,
            _types_namespace=_types_namespace,
        )
        if rebuilt:
            _compat.invalidate_validators(cls)
            for name, field in cls.model_fields.items():
                _check_annotation(field.annotation, name)
            _check_extra_annotation(cls)
        return rebuilt

    @classmethod
    def _check_names(cls, data: Mapping[str, object]) -> None:
        reserved = (
            set(dir(DictModel))
            | (set(dir(cls)) - set(cls.model_fields))
            | set(cls.model_computed_fields)
        )
        aliases = [
            field.serialization_alias or field.alias or name
            for name, field in cls.model_fields.items()
        ]
        if len(aliases) != len(set(aliases)):
            raise TypeError("pydandict_protected_name: ambiguous serialization aliases")
        for key in data:
            if not isinstance(key, str):  # pyright: ignore[reportUnnecessaryIsInstance]
                raise TypeError("pydandict_protected_name: model keys must be strings")
            if key.startswith("_") or key in reserved:
                raise TypeError(f"pydandict_protected_name: protected model/mapping name: {key}")
            if key not in cls.model_fields and key in aliases:
                raise TypeError(
                    f"pydandict_protected_name: extra collides with serialization alias: {key}"
                )

    def _ensure_alive(self) -> None:
        if _root(self) is not None and not object.__getattribute__(self, "_pd_alive"):
            raise RuntimeError("pydandict_stale_handle: stale owned model")

    def __getattribute__(self, name: str) -> object:
        if not name.startswith("_"):
            DictModel._ensure_alive(self)
        return super().__getattribute__(name)

    @property
    def model_fields_set(self) -> set[str]:
        return set(_compat.fields_set(self))

    @property
    def model_extra(self) -> dict[str, object] | None:
        extra = _compat.raw_extra(self)
        return dict(cast(Mapping[str, object], extra)) if extra is not None else None

    def __getitem__(self, key: str) -> object:
        self._ensure_alive()
        if not isinstance(key, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise KeyError(key)
        if key in type(self).model_fields:
            return _compat.raw_state(self)[key]
        return cast(Mapping[str, object], _compat.raw_extra(self) or {})[key]

    def __iter__(self) -> Iterator[str]:  # pyright: ignore[reportIncompatibleMethodOverride]
        # Intentional BaseModel pair-iteration divergence, required by Mapping.
        self._ensure_alive()
        version = _version(self, "_pd_version")
        keys = tuple(_data(self))

        def generate() -> Iterator[str]:
            for key in keys:
                self._ensure_alive()
                if _version(self, "_pd_version") != version:
                    raise RuntimeError(
                        "pydandict_iterator_invalidated: model keys changed during iteration"
                    )
                yield key

        return generate()

    def __len__(self) -> int:
        self._ensure_alive()
        return len(type(self).model_fields) + len(_compat.raw_extra(self) or {})

    def __contains__(self, key: object) -> bool:
        self._ensure_alive()
        return isinstance(key, str) and (
            key in type(self).model_fields or key in (_compat.raw_extra(self) or {})
        )

    def __repr__(self) -> str:
        self._ensure_alive()
        return super().__repr__()

    def __str__(self) -> str:
        self._ensure_alive()
        return super().__str__()

    def __eq__(self, other: object) -> bool:
        self._ensure_alive()
        if isinstance(other, DictModel):
            other._ensure_alive()
        return super().__eq__(other)

    def __setattr__(self, name: str, value: object) -> None:
        if _root(self) is None:
            object.__setattr__(self, name, value)
        elif name.startswith("_"):
            raise TypeError(
                "pydandict_unsupported_configuration: private writes are outside the DictModel API"
            )
        else:
            self[name] = value

    def __delattr__(self, name: str) -> None:
        try:
            del self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def _check_write(self, key: str, *, remove: bool = False, reset: bool = False) -> None:
        if not isinstance(key, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError("pydandict_protected_name: model keys must be strings")
        fields = type(self).model_fields
        if remove and key not in _data(self):
            raise KeyError(key)
        if reset and key not in _data(self):
            raise KeyError(key)
        if cast(Mapping[str, object], self.model_config).get("frozen") or (
            key in fields and fields[key].frozen
        ):
            _policy(self, "frozen_instance", key, "Frozen state cannot change")
        type(self)._check_names({key: None})  # pyright: ignore[reportPrivateUsage]
        if remove and key in fields:
            _policy(
                self,
                "pydandict_field_deletion",
                key,
                "Declared fields cannot be deleted",
            )
        if reset and (key not in fields or fields[key].is_required()):
            _policy(
                self,
                "pydandict_reset_required",
                key,
                "Reset requires a declared default",
            )
        if (
            not remove
            and not reset
            and key not in fields
            and self.model_config.get("extra") != "allow"
        ):
            _policy(self, "extra_forbidden", key, "Extra inputs are not permitted")

    def _check_ancestors(self, path: tuple[object, ...]) -> None:
        value: object = self
        for key in path:
            if isinstance(value, DictModel):
                if value.model_config.get("frozen") or (
                    isinstance(key, str)
                    and key in type(value).model_fields
                    and type(value).model_fields[key].frozen
                ):
                    _policy(
                        value, "frozen_instance", cast(str, key), "Frozen ancestor cannot change"
                    )
                value = _child(value, key)
            else:
                value = _child(value, key)

    def _ownership_coordinator(self) -> RootCoordinator:
        return RootCoordinator(
            self._container_change,
            self._input,
            self._detached,
            self._identity_handle_write,
            self._hash_input,
        )

    def _input(self, value: object) -> object:
        return _clone(value)

    def _hash_input(self, value: object) -> object:
        return _clone(value, hash_position=True)

    def _detached(self, value: object) -> object:
        """Return a usable detached copy for public guard copy operations."""
        return _own_result(_clone(value))

    def _identity_handle_write(self, handle: object) -> None:
        root = _root(self)
        if root is None:
            raise RuntimeError("pydandict_stale_handle: detached owned handle")
        if isinstance(handle, DictModel):
            handle._ensure_alive()
            path = _model_path(handle)
        elif isinstance(handle, Owned):
            guard = cast(Owned[Collection[object]], handle)
            guard.check_alive()
            path = cast(Path, _compat.slot_value(guard, "_path", ()))
        else:
            raise TypeError("pydandict_internal_handle: expected an owned handle")
        root._check_ancestors(path)

    def _transaction(
        self,
        target: DictModel | Owned[Collection[object]],
        operation: Callable[[object], tuple[R, set[Path]]],
    ) -> R:
        root = _root(self)
        if root is None:
            raise RuntimeError(
                "pydandict_unsupported_configuration: candidate mutation is unsupported"
            )
        self._ensure_alive()
        if _busy(root):
            raise RuntimeError("pydandict_reentrant_transaction: same root is already busy")
        object.__setattr__(root, "_pd_busy", True)
        try:
            origins: dict[int, object] = {}
            draft = _clone(root, origins)
            path = (
                _model_path(target)
                if isinstance(target, DictModel)
                else cast(Path, _compat.slot_value(target, "_path", ()))
            )
            result, changed = operation(_at(draft, path))
            if not changed:
                return result
            root._check_ancestors(path)
            absolute = {path + p for p in changed}
            # Mark fields on every affected model ancestor, preserving omitted defaults.
            for change in absolute:
                node = draft
                for key in change:
                    if isinstance(node, DictModel):
                        _compat.fields_set(node).add(cast(str, key))
                        node = _data(node).get(cast(str, key), _MISSING)
                    else:
                        try:
                            node = _child(node, key)
                        except (KeyError, IndexError, TypeError):
                            break
            # Reset/removal operations supply their final fields-set after ancestor marking.
            if isinstance(target, DictModel):
                local = cast(DictModel, _at(draft, path))
                explicit = cast(set[str] | None, _compat.slot_value(local, "_pd_reset", None))
                if explicit is not None:
                    _compat.set_fields_set(local, explicit)
            fault = type(root)._prototype_fault
            if fault:
                fault("staged")
            validated = _validate(_clone(draft))
            if fault:
                fault("validated")
            detached = _clone(result)
            detached = _own_result(detached)
            if fault:
                fault("result")
            updates = _prepare(root, draft, validated, origins, absolute)
            if fault:
                fault("prepared")
            _commit(updates)
            return cast(R, detached)
        finally:
            object.__setattr__(root, "_pd_busy", False)

    def _container_change(self, target: Owned[P], operation: Callable[[P], R]) -> R:
        def apply(data: object) -> tuple[R, set[Path]]:
            return operation(cast(P, data)), {()}

        return self._transaction(cast(Owned[Collection[object]], target), apply)

    def __setitem__(self, key: str, value: object) -> None:
        if (
            isinstance(key, str)  # pyright: ignore[reportUnnecessaryIsInstance]
            and key in _data(self)
            and _data(self)[key] is value
            and isinstance(value, (Owned, DictModel))
        ):
            self._ensure_alive()
            self._check_write(key)
            self._identity_handle_write(cast(object, value))
            return  # Python's augmented-assignment writeback of its committed handle.
        self.update({key: value})

    def update(
        self, other: _KeySource | Iterable[tuple[str, object]] = (), /, **kwargs: object
    ) -> None:
        def apply(value: object) -> tuple[object, set[Path]]:
            draft = cast(DictModel, value)
            patch = dict(other, **kwargs)
            # Structural key errors have precedence over per-key policy errors
            # for the complete staged batch (including frozen fields).
            if any(
                not isinstance(key, str)  # pyright: ignore[reportUnnecessaryIsInstance]
                for key in patch
            ):
                raise TypeError("pydandict_protected_name: model keys must be strings")
            for key in patch:
                self._check_write(key)
            values = _data(draft)
            values.update({key: _clone(value) for key, value in patch.items()})
            _compat.replace_storage(draft, values, draft.model_fields_set)
            return None, {(key,) for key in patch}

        self._transaction(self, apply)

    def __ior__(self, other: _KeySource | Iterable[tuple[str, object]]) -> Self:
        self.update(other)
        return self

    def __delitem__(self, key: str) -> None:
        def apply(input_value: object) -> tuple[object, set[Path]]:
            draft = cast(DictModel, input_value)
            self._check_write(key, remove=True)
            _extra_storage(draft).pop(key)
            _compat.fields_set(draft).discard(key)
            object.__setattr__(draft, "_pd_reset", draft.model_fields_set)
            return None, {(key,)}

        self._transaction(self, apply)

    def pop(self, key: str, default: object = _MISSING) -> object:
        # Mutation keys are canonical string names. Validate the key before
        # checking presence so a non-string key cannot silently return a
        # caller-supplied fallback (unlike read-side ``get`` semantics).
        if not isinstance(key, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError("pydandict_protected_name: model keys must be strings")

        def apply(input_value: object) -> tuple[object, set[Path]]:
            draft = cast(DictModel, input_value)
            if key not in _data(self):
                if default is _MISSING:
                    raise KeyError(key)
                return default, set()
            self._check_write(key, remove=True)
            value = _extra_storage(draft).pop(key)
            _compat.fields_set(draft).discard(key)
            object.__setattr__(draft, "_pd_reset", draft.model_fields_set)
            return value, {(key,)}

        return self._transaction(self, apply)

    def popitem(self) -> tuple[str, object]:
        keys = tuple(self)
        if not keys:
            raise KeyError("empty model")
        key = keys[-1]
        return key, self.pop(key)

    def clear(self) -> None:
        def apply(input_value: object) -> tuple[object, set[Path]]:
            draft = cast(DictModel, input_value)
            keys = tuple(self)
            for key in keys:
                self._check_write(key, remove=True)
            if not keys:
                return None, set()
            _extra_storage(draft).clear()
            object.__setattr__(draft, "_pd_reset", set())
            return None, {(key,) for key in keys}

        self._transaction(self, apply)

    def setdefault(self, key: str, default: object = None) -> object:
        if key in self:
            return self[key]
        self[key] = default
        return self[key]

    def reset(self, *field_names: str) -> None:
        def apply(input_value: object) -> tuple[object, set[Path]]:
            draft = cast(DictModel, input_value)
            names = tuple(dict.fromkeys(field_names))
            if any(
                not isinstance(key, str)  # pyright: ignore[reportUnnecessaryIsInstance]
                for key in names
            ):
                raise TypeError("pydandict_protected_name: model keys must be strings")
            for key in names:
                self._check_write(key, reset=True)
            explicit = draft.model_fields_set - set(names)
            for key in names:
                _compat.raw_state(draft).pop(key)
            object.__setattr__(draft, "_pd_reset", explicit)
            return None, {(key,) for key in names}

        self._transaction(self, apply)

    def model_copy(self, *, update: Mapping[str, object] | None = None, deep: bool = False) -> Self:
        root = _root(self)
        self._ensure_alive()
        if root is not None and _busy(root):
            raise RuntimeError("pydandict_reentrant_transaction: same root copy is already busy")
        if root is not None:
            object.__setattr__(root, "_pd_busy", True)
        try:
            raw = _clone(self)
            if update:
                type(self)._check_names(update)
                for key in update:
                    if (
                        key not in type(self).model_fields
                        and self.model_config.get("extra") != "allow"
                    ):
                        _policy(
                            self,
                            "extra_forbidden",
                            key,
                            "Extra inputs are not permitted",
                        )
                values = _data(raw)
                values.update(cast(dict[str, object], _clone(dict(update))))
                raw = _blank(type(self), values, raw.model_fields_set | set(update))
            validated = _validate(raw)
            for key, value in _data(raw).items():
                if key not in (update or {}) and _fingerprint(value) != _fingerprint(
                    _data(validated)[key]
                ):
                    raise TypeError(
                        f"pydandict_canonical_drift: canonical copy changed untouched field {key!r}"
                    )
            return _install(validated)
        finally:
            if root is not None:
                object.__setattr__(root, "_pd_busy", False)

    def __copy__(self) -> Self:
        return self.model_copy()

    def __deepcopy__(self, memo: dict[int, object] | None = None) -> Self:
        return self.model_copy(deep=True)

    @classmethod
    def model_construct(cls, _fields_set: set[str] | None = None, **values: object) -> Self:
        raise TypeError(
            "pydandict_trusted_path_disabled: use model_validate; trusted construction is disabled"
        )

    def copy(
        self,
        *,
        include: object = None,
        exclude: object = None,
        update: dict[str, object] | None = None,
        deep: bool = False,
    ) -> Self:
        import warnings

        warnings.warn("copy is deprecated; use model_copy", DeprecationWarning, stacklevel=2)
        if include is not None or exclude is not None:
            raise TypeError("pydandict_trusted_path_disabled: partial model copies are unsupported")
        return self.model_copy(update=update, deep=deep)

    def __reduce_ex__(self, protocol: SupportsIndex) -> Any:
        raise TypeError(
            "pydandict_trusted_path_disabled: pickle is outside the DictModel ownership contract"
        )


def _own_result(value: object) -> object:
    if isinstance(value, DictModel):
        return _install(_validate(value))
    if isinstance(value, list):
        return [_own_result(v) for v in cast(list[object], value)]
    if isinstance(value, (dict, OwnedDict)):
        return {k: _own_result(v) for k, v in cast(Mapping[object, object], value).items()}
    if isinstance(value, tuple):
        return tuple(_own_result(v) for v in cast(tuple[object, ...], value))
    return value
