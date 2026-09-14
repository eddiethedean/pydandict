"""Pydandict model/mapping implementation for the Phase 0.1 release baseline.

Version-sensitive Pydantic extraction/validation/serialization is deliberately
concentrated here. Ownership uses pointer-swap commits and raw-state snapshots.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, MutableMapping
from contextvars import ContextVar
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any, ClassVar, LiteralString, Protocol, Self, SupportsIndex, cast
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    GetCoreSchemaHandler,
    PydanticUserError,
    ValidationError,
)
from pydantic.config import ExtraValues
from pydantic_core import CoreSchema, PydanticCustomError, SchemaValidator, core_schema

from ._containers import Owned, OwnedDict, OwnedList, OwnedSet

_BUILDING: ContextVar[bool] = ContextVar("pydandict_building", default=False)
_CANONICAL: ContextVar[bool] = ContextVar("pydandict_canonical", default=False)
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


def _root(value: Any) -> Any:
    try:
        return object.__getattribute__(value, "_pd_root")
    except AttributeError:
        return None


def _data(model: Any) -> dict[str, Any]:
    fields = type(model).model_fields
    data = {k: v for k, v in object.__getattribute__(model, "__dict__").items() if k in fields}
    data.update(object.__getattribute__(model, "__pydantic_extra__") or {})
    return data


def _blank(cls: Any, data: dict[str, Any], fields_set: set[str]) -> Any:
    # Internal trusted snapshot only; never exposed until validated/owned.
    obj = object.__new__(cls)
    fields = cls.model_fields
    object.__setattr__(obj, "__dict__", {k: v for k, v in data.items() if k in fields})
    object.__setattr__(
        obj,
        "__pydantic_extra__",
        {k: v for k, v in data.items() if k not in fields}
        if cls.model_config.get("extra") == "allow"
        else None,
    )
    object.__setattr__(obj, "__pydantic_fields_set__", set(fields_set))
    object.__setattr__(obj, "__pydantic_private__", None)
    return obj


def _clone(
    value: Any, origins: dict[int, Any] | None = None, active: set[int] | None = None
) -> Any:
    if type(value) in _IMMUTABLE:
        return value
    if active is None:
        active = set()
    identity = id(value)
    if identity in active:
        raise TypeError("cyclic values are outside the Phase 0.1 ownership envelope")
    active.add(identity)
    try:
        if isinstance(value, DictModel):
            value._ensure_alive()
            result = _blank(
                type(value),
                {k: _clone(v, origins, active) for k, v in _data(value).items()},
                value.model_fields_set,
            )
        elif type(value) in (list, OwnedList):
            result = [_clone(v, origins, active) for v in value]
        elif type(value) in (dict, OwnedDict):
            result = {_clone(k, None, active): _clone(v, origins, active) for k, v in value.items()}
        elif type(value) in (set, OwnedSet):
            result = {_clone(v, None, active) for v in value}
        elif type(value) is tuple:
            result = tuple(_clone(v, origins, active) for v in value)
        elif type(value) is frozenset:
            result = frozenset(_clone(v, None, active) for v in value)
        else:
            raise TypeError(f"unsupported owned value: {type(value).__name__}")
        if origins is not None and (isinstance(value, Owned) or _root(value) is not None):
            origins[id(result)] = value
        return result
    finally:
        active.remove(identity)


def _fingerprint(value: Any) -> Any:
    # No user-defined equality/hash methods are called. The envelope is closed.
    if isinstance(value, DictModel):
        return (
            type(value),
            tuple((k, _fingerprint(v)) for k, v in _data(value).items()),
        )
    if isinstance(value, (list, tuple, OwnedList)):
        return ("sequence", tuple(_fingerprint(v) for v in value))
    if isinstance(value, (dict, OwnedDict)):
        return (
            "dict",
            tuple((_fingerprint(k), _fingerprint(v)) for k, v in value.items()),
        )
    if isinstance(value, (set, frozenset, OwnedSet)):
        return ("set", frozenset(_fingerprint(v) for v in value))
    if type(value) not in _IMMUTABLE:
        raise TypeError(f"unsupported validated value: {type(value).__name__}")
    # repr handles NaN without an unequal-to-itself drift check.
    return (type(value), repr(value))


def _at(value: Any, path: tuple[Any, ...]) -> Any:
    for part in path:
        value = _data(value)[part] if isinstance(value, DictModel) else value[part]
    return value


def _policy(model: Any, code: LiteralString, key: Any, message: LiteralString) -> None:
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


def _canonical_schema(value: Any) -> Any:
    # The tested upstream wrap handler drops call-time alias overrides. A copied
    # Pydantic core schema removes input aliases for internal canonical snapshots.
    # Public constructors/serializers keep the original generated schema.
    if isinstance(value, (dict, OwnedDict)):
        return {
            k: _canonical_schema(v)
            for k, v in value.items()
            if not (value.get("type") == "model-field" and k == "validation_alias")
        }
    if isinstance(value, list):
        return [_canonical_schema(v) for v in value]
    return value


def _validate(candidate: Any) -> Any:
    token = _BUILDING.set(True)
    canonical_token = _CANONICAL.set(True)
    try:
        cls = type(candidate)
        validator = cls.__dict__.get("_pd_canonical_validator")
        if validator is None:
            validator = SchemaValidator(_canonical_schema(cls.__pydantic_core_schema__))
            cls._pd_canonical_validator = validator
        return validator.validate_python(candidate)
    finally:
        _CANONICAL.reset(canonical_token)
        _BUILDING.reset(token)


def _walk(value: Any, path: tuple[Any, ...] = ()):
    if isinstance(value, (DictModel, Owned)):
        yield value, path
    if isinstance(value, DictModel):
        for key, child in _data(value).items():
            yield from _walk(child, path + (key,))
    elif isinstance(value, (list, tuple, OwnedList)):
        for key, child in enumerate(value):
            yield from _walk(child, path + (key,))
    elif isinstance(value, (dict, OwnedDict)):
        for key, child in value.items():
            yield from _walk(child, path + (key,))


def _prepare(
    root: Any,
    expected: Any,
    validated: Any,
    origins: dict[int, Any],
    changed: set[tuple[Any, ...]],
):
    updates: list[tuple[Any, str, Any]] = []
    retained: set[int] = set()
    nodes: list[Any] = []

    def prepare(before: Any, after: Any, path: tuple[Any, ...]) -> Any:
        old = origins.get(id(before))
        descendant_change = any(p[: len(path)] == path for p in changed)
        affected = descendant_change or any(path[: len(p)] == p for p in changed)
        check_untouched = before is not _MISSING and (
            not affected or (old is not None and not descendant_change)
        )
        if check_untouched and _fingerprint(before) != _fingerprint(after):
            raise TypeError(
                f"canonical revalidation changed untouched state at {path!r}; "
                "use idempotent validators"
            )
        if isinstance(after, DictModel):
            if old is not None and type(old) is not type(after):
                old = None
            target = old if old is not None else _blank(type(after), {}, set())
            before_data = _data(before) if isinstance(before, DictModel) else {}
            after_data = _data(after)
            type(after)._check_names(after_data)
            values = {
                k: prepare(before_data.get(k, _MISSING), v, path + (k,))
                for k, v in after_data.items()
            }
            fields = type(after).model_fields
            previous_keys = tuple(_data(target))
            updates.extend(
                [
                    (
                        target,
                        "__dict__",
                        {k: v for k, v in values.items() if k in fields},
                    ),
                    (
                        target,
                        "__pydantic_extra__",
                        {k: v for k, v in values.items() if k not in fields}
                        if type(after).model_config.get("extra") == "allow"
                        else None,
                    ),
                    (target, "__pydantic_fields_set__", set(after.model_fields_set)),
                    (target, "_pd_root", root),
                    (target, "_pd_alive", True),
                    (target, "_pd_path", path),
                    (
                        target,
                        "_pd_version",
                        getattr(target, "_pd_version", 0) + (tuple(values) != previous_keys),
                    ),
                ]
            )
        elif type(after) in (list, dict, set):
            cls = {list: OwnedList, dict: OwnedDict, set: OwnedSet}[type(after)]
            if old is not None and type(old) is not cls:
                old = None
            target = old if old is not None else cls()
            if isinstance(after, list):
                previous = before if isinstance(before, list) else []
                if old is not None and len(previous) != len(after):
                    raise TypeError(
                        "validator changed owned list topology; use topology-preserving validators"
                    )
                values = [
                    prepare(previous[i] if i < len(previous) else _MISSING, v, path + (i,))
                    for i, v in enumerate(after)
                ]
            elif isinstance(after, dict):
                previous = before if isinstance(before, dict) else {}
                if old is not None and tuple(previous) != tuple(after):
                    raise TypeError("validator changed owned dictionary topology")
                values = {
                    _clone(k): prepare(previous.get(k, _MISSING), v, path + (k,))
                    for k, v in after.items()
                }
            else:
                values = {_clone(v) for v in after}
            updates.extend(
                [
                    (target, "_data", values),
                    (target, "_root", root),
                    (target, "_alive", True),
                    (target, "_path", path),
                    (target, "_version", getattr(target, "_version", 0) + 1),
                ]
            )
        elif type(after) is tuple:
            previous = before if isinstance(before, tuple) else ()
            return tuple(
                prepare(previous[i] if i < len(previous) else _MISSING, v, path + (i,))
                for i, v in enumerate(after)
            )
        else:
            return _clone(after)
        if old is not None:
            retained.add(id(old))
        nodes.append(target)
        return target

    result = prepare(expected, validated, ())
    assert result is root
    for node in getattr(root, "_pd_nodes", ()):
        if id(node) not in retained:
            updates.append((node, "_pd_alive" if isinstance(node, DictModel) else "_alive", False))
    updates.append((root, "_pd_nodes", tuple(nodes)))
    return updates


def _swap(target: Any, name: str, value: Any) -> None:
    object.__setattr__(target, name, value)


def _commit(updates: list[tuple[Any, str, Any]]) -> None:
    # Hold old state through every swap; no owned payload is destroyed mid-commit.
    undo = [(target, name, getattr(target, name, _MISSING)) for target, name, _ in updates]
    try:
        for target, name, value in updates:
            _swap(target, name, value)
    except BaseException:
        for target, name, value in reversed(undo):
            if value is _MISSING:
                try:
                    object.__delattr__(target, name)
                except AttributeError:
                    pass
            else:
                object.__setattr__(target, name, value)
        raise


def _install(value: Any) -> Any:
    if value.__pydantic_extra__ and type(value).model_config.get("extra") != "allow":
        raise TypeError("construction extra override conflicts with ongoing class policy")
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
    _prototype_fault: ClassVar[Any] = None

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[BaseModel], handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        schema = dict(handler(source))
        schema_ref = schema.pop("ref", None)

        def finish(value: Any, next_validator: Any) -> Any:
            if _BUILDING.get():
                if isinstance(value, DictModel):
                    if not _CANONICAL.get():
                        return _validate(value)
                    result = next_validator(_data(value))
                    object.__setattr__(result, "__pydantic_fields_set__", value.model_fields_set)
                    return result
                return next_validator(value)
            if isinstance(value, DictModel):
                return _install(_validate(_clone(value)))
            # Detach inputs before user validation, not only after construction.
            token = _BUILDING.set(True)
            try:
                validated = next_validator(_clone(value))
            finally:
                _BUILDING.reset(token)
            return _install(validated)

        def serialize(value: Any, next_serializer: Any, info: Any) -> Any:
            value._ensure_alive()
            return next_serializer(_clone(value))

        return core_schema.no_info_wrap_validator_function(
            finish,
            cast(CoreSchema, schema),
            ref=cast(str | None, schema_ref),
            serialization=core_schema.wrap_serializer_function_ser_schema(serialize, info_arg=True),
        )

    @classmethod
    def _entry_validator(cls, by_alias: bool | None, by_name: bool | None) -> Any:
        if by_alias is False and by_name is not True:
            raise PydanticUserError(
                "At least one of by_alias or by_name must be True",
                code="validate-by-alias-and-name-false",
            )
        if by_alias is None and by_name is None:
            return cls.__pydantic_validator__
        cache = cls.__dict__.get("_pd_alias_validators")
        if cache is None:
            cache = {}
            cls._pd_alias_validators = cache
        key = (by_alias, by_name)
        if key not in cache:

            def adjust(value: Any) -> Any:
                if isinstance(value, dict):
                    result = {k: adjust(v) for k, v in value.items()}
                    if value.get("type") == "model":
                        config = dict(result.get("config", {}))
                        if by_name is not None:
                            config["validate_by_name"] = by_name
                        if by_alias is not None:
                            config["validate_by_alias"] = by_alias
                        result["config"] = config
                    return result
                if isinstance(value, list):
                    return [adjust(v) for v in value]
                return value

            cache[key] = SchemaValidator(adjust(cls.__pydantic_core_schema__))
        return cache[key]

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
        return cls._entry_validator(by_alias, by_name).validate_strings(
            obj, strict=strict, extra=extra, context=context
        )

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        if not cls.model_config.get("validate_assignment") or not cls.model_config.get(
            "validate_default"
        ):
            raise TypeError("validation cannot be disabled")
        if cls.model_config.get("revalidate_instances") != "always":
            raise TypeError("DictModel requires revalidate_instances='always'")
        for field in cls.model_fields.values():
            if field.validate_default is False:
                raise TypeError("default validation cannot be disabled")
        if cls.__private_attributes__:
            raise TypeError("private attributes are not supported by DictModel")
        if cls.model_post_init is not BaseModel.model_post_init:
            raise TypeError("model_post_init is outside the supported hook contract")
        if cls.__init__ is not BaseModel.__init__ or "__del__" in cls.__dict__:
            raise TypeError("custom initialization/finalization is unsupported")
        if any(
            isinstance(value, property) and value.fset is not None
            for value in cls.__dict__.values()
        ):
            raise TypeError("writable properties are outside the DictModel transaction API")
        cls._check_names(cls.model_fields)

    @classmethod
    def _check_names(cls, data: Mapping[str, Any]) -> None:
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
            raise TypeError("ambiguous serialization aliases")
        for key in data:
            if not isinstance(key, str):
                raise TypeError("model keys must be strings")
            if key.startswith("_") or key in reserved:
                raise TypeError(f"protected model/mapping name: {key}")
            if key not in cls.model_fields and key in aliases:
                raise TypeError(f"extra collides with serialization alias: {key}")

    def _ensure_alive(self) -> None:
        if _root(self) is not None and not object.__getattribute__(self, "_pd_alive"):
            raise RuntimeError("stale owned model")

    def __getattribute__(self, name: str) -> Any:
        if not name.startswith("_"):
            DictModel._ensure_alive(self)
        return super().__getattribute__(name)

    @property
    def model_fields_set(self) -> set[str]:
        return set(object.__getattribute__(self, "__pydantic_fields_set__"))

    @property
    def model_extra(self) -> dict[str, Any] | None:
        extra = object.__getattribute__(self, "__pydantic_extra__")
        return dict(extra) if extra is not None else None

    def __getitem__(self, key: str) -> object:
        self._ensure_alive()
        if not isinstance(key, str):
            raise KeyError(key)
        if key in type(self).model_fields:
            return object.__getattribute__(self, "__dict__")[key]
        return (object.__getattribute__(self, "__pydantic_extra__") or {})[key]

    def __iter__(self) -> Iterator[str]:  # pyright: ignore[reportIncompatibleMethodOverride]
        # Intentional BaseModel pair-iteration divergence, required by Mapping.
        self._ensure_alive()
        version = getattr(self, "_pd_version", 0)
        keys = tuple(_data(self))

        def generate() -> Iterator[str]:
            for key in keys:
                self._ensure_alive()
                if getattr(self, "_pd_version", 0) != version:
                    raise RuntimeError("model keys changed during iteration")
                yield key

        return generate()

    def __len__(self) -> int:
        self._ensure_alive()
        return len(type(self).model_fields) + len(
            object.__getattribute__(self, "__pydantic_extra__") or {}
        )

    def __contains__(self, key: object) -> bool:
        self._ensure_alive()
        return isinstance(key, str) and (
            key in type(self).model_fields
            or key in (object.__getattribute__(self, "__pydantic_extra__") or {})
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

    def __setattr__(self, name: str, value: Any) -> None:
        if _root(self) is None:
            object.__setattr__(self, name, value)
        elif name.startswith("_"):
            raise TypeError("private writes are outside the DictModel API")
        else:
            self[name] = value

    def __delattr__(self, name: str) -> None:
        try:
            del self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def _check_write(self, key: str, *, remove: bool = False, reset: bool = False) -> None:
        if not isinstance(key, str):
            raise TypeError("model keys must be strings")
        fields = type(self).model_fields
        if remove and key not in _data(self):
            raise KeyError(key)
        if reset and key not in _data(self):
            raise KeyError(key)
        if self.model_config.get("frozen") or (key in fields and fields[key].frozen):
            _policy(self, "frozen_instance", key, "Frozen state cannot change")
        type(self)._check_names({key: None})
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

    def _check_ancestors(self, path: tuple[Any, ...]) -> None:
        value: Any = self
        for key in path:
            if isinstance(value, DictModel):
                if value.model_config.get("frozen") or (
                    key in type(value).model_fields and type(value).model_fields[key].frozen
                ):
                    _policy(value, "frozen_instance", key, "Frozen ancestor cannot change")
                value = _data(value)[key]
            else:
                value = value[key]

    def _input(self, value: Any) -> Any:
        return _clone(value)

    def _transaction(self, target: Any, operation: Any) -> Any:
        root = _root(self)
        if root is None:
            raise RuntimeError("candidate mutation is unsupported")
        self._ensure_alive()
        if root._pd_busy:
            raise RuntimeError("reentrant transaction on the same root")
        object.__setattr__(root, "_pd_busy", True)
        try:
            origins: dict[int, Any] = {}
            draft = _clone(root, origins)
            path = target._pd_path if isinstance(target, DictModel) else target._path
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
                        object.__getattribute__(node, "__pydantic_fields_set__").add(key)
                        node = _data(node).get(key, _MISSING)
                    else:
                        try:
                            node = node[key]
                        except (KeyError, IndexError, TypeError):
                            break
            # Reset/removal operations supply their final fields-set after ancestor marking.
            if isinstance(target, DictModel):
                local = _at(draft, path)
                explicit = getattr(local, "_pd_reset", None)
                if explicit is not None:
                    object.__setattr__(local, "__pydantic_fields_set__", explicit)
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
            return detached
        finally:
            object.__setattr__(root, "_pd_busy", False)

    def _container_change(self, target: Any, operation: Any) -> Any:
        def apply(data: Any):
            return operation(data), {()}

        return self._transaction(target, apply)

    def __setitem__(self, key: str, value: object) -> None:
        if (
            isinstance(key, str)
            and key in _data(self)
            and _data(self)[key] is value
            and isinstance(value, (Owned, DictModel))
        ):
            self._ensure_alive()
            self._check_write(key)
            return  # Python's augmented-assignment writeback of its committed handle.
        self.update({key: value})

    def update(
        self, other: _KeySource | Iterable[tuple[str, object]] = (), /, **kwargs: object
    ) -> None:
        def apply(draft: Any):
            patch = dict(other, **kwargs)
            for key in patch:
                self._check_write(key)
            values = _data(draft)
            values.update({key: _clone(value) for key, value in patch.items()})
            replacement = _blank(type(draft), values, draft.model_fields_set)
            object.__setattr__(draft, "__dict__", replacement.__dict__)
            object.__setattr__(draft, "__pydantic_extra__", replacement.__pydantic_extra__)
            return None, {(key,) for key in patch}

        self._transaction(self, apply)

    def __ior__(self, other: _KeySource | Iterable[tuple[str, object]]) -> Self:
        self.update(other)
        return self

    def __delitem__(self, key: str) -> None:
        def apply(draft: Any):
            self._check_write(key, remove=True)
            draft.__pydantic_extra__.pop(key)
            object.__getattribute__(draft, "__pydantic_fields_set__").discard(key)
            object.__setattr__(draft, "_pd_reset", draft.model_fields_set)
            return None, {(key,)}

        self._transaction(self, apply)

    def pop(self, key: str, default: object = _MISSING) -> object:
        def apply(draft: Any):
            if key not in _data(self):
                if default is _MISSING:
                    raise KeyError(key)
                return default, set()
            self._check_write(key, remove=True)
            value = draft.__pydantic_extra__.pop(key)
            object.__getattribute__(draft, "__pydantic_fields_set__").discard(key)
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
        def apply(draft: Any):
            keys = tuple(self)
            for key in keys:
                self._check_write(key, remove=True)
            if not keys:
                return None, set()
            draft.__pydantic_extra__.clear()
            object.__setattr__(draft, "_pd_reset", set())
            return None, {(key,) for key in keys}

        self._transaction(self, apply)

    def setdefault(self, key: str, default: object = None) -> object:
        if key in self:
            return self[key]
        self[key] = default
        return self[key]

    def reset(self, *field_names: str) -> None:
        def apply(draft: Any):
            names = tuple(dict.fromkeys(field_names))
            for key in names:
                self._check_write(key, reset=True)
            explicit = draft.model_fields_set - set(names)
            for key in names:
                draft.__dict__.pop(key)
            object.__setattr__(draft, "_pd_reset", explicit)
            return None, {(key,) for key in names}

        self._transaction(self, apply)

    def model_copy(self, *, update: Mapping[str, Any] | None = None, deep: bool = False) -> Self:
        root = _root(self)
        self._ensure_alive()
        if root is not None and root._pd_busy:
            raise RuntimeError("reentrant copy on the same root")
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
                values.update(_clone(dict(update)))
                raw = _blank(type(self), values, raw.model_fields_set | set(update))
            validated = _validate(raw)
            for key, value in _data(raw).items():
                if key not in (update or {}) and _fingerprint(value) != _fingerprint(
                    _data(validated)[key]
                ):
                    raise TypeError(f"canonical copy changed untouched field {key!r}")
            return _install(validated)
        finally:
            if root is not None:
                object.__setattr__(root, "_pd_busy", False)

    def __copy__(self) -> Self:
        return self.model_copy()

    def __deepcopy__(self, memo: dict[int, Any] | None = None) -> Self:
        return self.model_copy(deep=True)

    @classmethod
    def model_construct(cls, _fields_set: set[str] | None = None, **values: Any) -> Self:
        raise TypeError("use model_validate; trusted construction is disabled")

    def copy(
        self,
        *,
        include: Any = None,
        exclude: Any = None,
        update: dict[str, Any] | None = None,
        deep: bool = False,
    ) -> Self:
        import warnings

        warnings.warn("copy is deprecated; use model_copy", DeprecationWarning, stacklevel=2)
        if include is not None or exclude is not None:
            raise TypeError("partial model copies are unsupported")
        return self.model_copy(update=update, deep=deep)

    def __reduce_ex__(self, protocol: SupportsIndex) -> Any:
        raise TypeError("pickle is outside the DictModel ownership contract")


def _own_result(value: Any) -> Any:
    if isinstance(value, DictModel):
        return _install(_validate(value))
    if isinstance(value, list):
        return [_own_result(v) for v in value]
    if isinstance(value, (dict, OwnedDict)):
        return {k: _own_result(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return tuple(_own_result(v) for v in value)
    return value
