"""Private protocol handles with one authoritative payload per owned node.

Concrete built-in subclasses were rejected: C consumers can bypass their overrides
and silently read an unused base buffer. These ABC guards have no such buffer.
The model serializer delegates with a raw snapshot so field serializers still work.
"""

from __future__ import annotations

from collections.abc import (
    Collection,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    Mapping,
    MutableMapping,
    MutableSequence,
    MutableSet,
    ValuesView,
)
from collections.abc import Set as AbstractSet
from typing import Callable, Generic, Protocol, Self, TypeVar, cast, overload

P = TypeVar("P", bound=Collection[object])
R = TypeVar("R")
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")
D = TypeVar("D")
Path = tuple[object, ...]


K_co = TypeVar("K_co")
V_co = TypeVar("V_co", covariant=True)


class KeySource(Protocol[K_co, V_co]):
    def keys(self) -> Iterable[K_co]: ...
    def __getitem__(self, key: K_co, /) -> V_co: ...


class Change(Protocol):
    def __call__(self, target: Owned[P], operation: Callable[[P], R]) -> R: ...


class RootCoordinator:
    """A private package collaborator with explicitly typed callbacks."""

    def __init__(
        self,
        change: Change,
        input_value: Callable[[object], object],
        detached: Callable[[object], object],
        identity_write: Callable[[object], None],
        hash_input: Callable[[object], object],
    ):
        self.change = change
        self.input_value = input_value
        self.detached = detached
        self.identity_write = identity_write
        self.hash_input = hash_input


class Owned(Generic[P]):
    _data: P
    _root: RootCoordinator
    _alive: bool
    _path: tuple[object, ...]
    _version: int

    def check_alive(self) -> None:
        if not self._alive:
            raise RuntimeError("pydandict_stale_handle: stale owned handle")

    def read_payload(self) -> P:
        self.check_alive()
        return self._data

    def _change(self, operation: Callable[[P], R]) -> R:
        self.check_alive()
        return self._root.change(self, operation)

    def _iterate(self, values: Iterable[T]) -> Iterator[T]:
        self.check_alive()
        version = self._version
        iterator = iter(values)

        def generate() -> Iterator[T]:
            while True:
                self.check_alive()
                if self._version != version:
                    raise RuntimeError(
                        "pydandict_iterator_invalidated: owned container changed during iteration"
                    )
                try:
                    item = next(iterator)
                except StopIteration:
                    return
                yield item

        return generate()

    def __len__(self) -> int:
        return len(self.read_payload())

    def __repr__(self) -> str:
        return repr(self.read_payload())

    def __str__(self) -> str:
        return str(self.read_payload())

    def __contains__(self, value: object) -> bool:
        return value in self.read_payload()

    def __eq__(self, other: object) -> bool:
        return self.read_payload() == read(other)

    def __ne__(self, other: object) -> bool:
        return self.read_payload() != read(other)


def read(value: object) -> object:
    return (
        cast(Owned[Collection[object]], value).read_payload() if isinstance(value, Owned) else value
    )


def _is_owned_handle(value: object) -> bool:
    if isinstance(value, Owned):
        return True
    try:
        return object.__getattribute__(value, "_pd_root") is not None
    except AttributeError:
        return False


def _check_owned_handle(value: object) -> None:
    if isinstance(value, Owned):
        cast(Owned[Collection[object]], value).check_alive()


class OwnedList(Owned[list[T]], MutableSequence[T]):
    def __iter__(self) -> Iterator[T]:
        return self._iterate(self.read_payload())

    def __reversed__(self) -> Iterator[T]:
        return self._iterate(reversed(self.read_payload()))

    @overload
    def __getitem__(self, key: int) -> T: ...
    @overload
    def __getitem__(self, key: slice) -> list[T]: ...
    def __getitem__(self, key: int | slice) -> T | list[T]:
        return self.read_payload()[key]

    @overload
    def __setitem__(self, key: int, value: T) -> None: ...
    @overload
    def __setitem__(self, key: slice, value: Iterable[T]) -> None: ...
    def __setitem__(self, key: int | slice, value: T | Iterable[T]) -> None:
        if isinstance(key, slice):
            self._change(
                lambda data: data.__setitem__(
                    key,
                    cast(
                        list[T],
                        self._root.input_value(list(cast(Iterable[T], value))),
                    ),
                )
            )
        elif self.read_payload()[key] is value and _is_owned_handle(value):
            _check_owned_handle(value)
            self._root.identity_write(value)
        else:
            self._change(lambda data: data.__setitem__(key, cast(T, self._root.input_value(value))))

    def __delitem__(self, key: int | slice) -> None:
        self._change(lambda data: data.__delitem__(key))

    def append(self, value: T) -> None:
        self._change(lambda data: data.append(cast(T, self._root.input_value(value))))

    def extend(self, values: Iterable[T]) -> None:
        self._change(lambda data: data.extend(cast(list[T], self._root.input_value(list(values)))))

    def insert(self, index: int, value: T) -> None:
        self._change(lambda data: data.insert(index, cast(T, self._root.input_value(value))))

    def pop(self, index: int = -1) -> T:
        return self._change(lambda data: data.pop(index))

    def remove(self, value: T) -> None:
        self._change(lambda data: data.remove(value))

    def clear(self) -> None:
        self._change(lambda data: data.clear())

    def reverse(self) -> None:
        self._change(lambda data: data.reverse())

    def sort(self, *, key: Callable[[T], object] | None = None, reverse: bool = False) -> None:
        self._change(
            lambda data: (
                cast(list[_Comparable], data).sort(reverse=reverse)
                if key is None
                else data.sort(key=cast(Callable[[T], _Comparable], key), reverse=reverse)
            )
        )

    def __iadd__(self, values: Iterable[T]) -> Self:
        self.extend(values)
        return self

    def __imul__(self, count: int) -> Self:
        # Repeated mutable elements must be independently owned, not aliased.
        def multiply(data: list[T]) -> None:
            original = list(data)
            data *= count
            if count > 1:
                data[len(original) :] = [
                    cast(T, self._root.input_value(v)) for v in data[len(original) :]
                ]

        self._change(multiply)
        return self

    def copy(self) -> list[T]:
        return list(self)

    def __copy__(self) -> list[T]:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, object] | None = None) -> list[T]:
        return cast(list[T], self._root.detached(self))

    def count(self, value: T) -> int:
        return self.read_payload().count(value)

    def index(self, value: T, start: int = 0, stop: int = 9223372036854775807) -> int:
        return self.read_payload().index(value, start, stop)

    def __add__(self, other: list[T] | OwnedList[T]) -> list[T]:
        return self.read_payload() + cast(list[T], read(other))

    def __radd__(self, other: list[T] | OwnedList[T]) -> list[T]:
        return cast(list[T], read(other)) + self.read_payload()

    def __mul__(self, count: int) -> list[T]:
        return self.read_payload() * count

    def __rmul__(self, count: int) -> list[T]:
        return self * count

    def __lt__(self, other: list[T] | OwnedList[T]) -> bool:
        return self.read_payload() < cast(list[T], read(other))

    def __le__(self, other: list[T] | OwnedList[T]) -> bool:
        return self.read_payload() <= cast(list[T], read(other))

    def __gt__(self, other: list[T] | OwnedList[T]) -> bool:
        return self.read_payload() > cast(list[T], read(other))

    def __ge__(self, other: list[T] | OwnedList[T]) -> bool:
        return self.read_payload() >= cast(list[T], read(other))


class _Comparable(Protocol):
    def __lt__(self, other: object, /) -> bool: ...


class OwnedDict(Owned[dict[K, V]], MutableMapping[K, V]):
    def __iter__(self) -> Iterator[K]:
        return self._iterate(self.read_payload())

    def __reversed__(self) -> Iterator[K]:
        return self._iterate(reversed(self.read_payload()))

    def __getitem__(self, key: K) -> V:
        return self.read_payload()[key]

    def __setitem__(self, key: K, value: V) -> None:
        self.check_alive()
        key = cast(K, self._root.hash_input(key))
        if (
            key in self.read_payload()
            and self.read_payload()[key] is value
            and _is_owned_handle(value)
        ):
            _check_owned_handle(value)
            self._root.identity_write(value)
            return
        self._change(lambda data: data.__setitem__(key, cast(V, self._root.input_value(value))))

    def __delitem__(self, key: K) -> None:
        self._change(lambda data: data.__delitem__(key))

    @overload
    def get(self, key: K, /) -> V | None: ...
    @overload
    def get(self, key: K, default: V, /) -> V: ...
    @overload
    def get(self, key: K, default: D, /) -> V | D: ...
    def get(self, key: K, default: D | None = None) -> V | D | None:
        return self.read_payload().get(key, default)

    def keys(self) -> KeysView[K]:
        from collections.abc import KeysView

        return KeysView(self)

    def values(self) -> ValuesView[V]:
        from collections.abc import ValuesView

        return ValuesView(self)

    def items(self) -> ItemsView[K, V]:
        from collections.abc import ItemsView

        return ItemsView(self)

    @overload
    def update(self, other: KeySource[K, V], /, **kwargs: V) -> None: ...
    @overload
    def update(self, other: Iterable[tuple[K, V]] = (), /, **kwargs: V) -> None: ...
    def update(self, other: KeySource[K, V] | Iterable[tuple[K, V]] = (), /, **kwargs: V) -> None:
        def apply(data: dict[K, V]) -> None:
            source: Iterable[tuple[K, V]]
            if isinstance(other, Mapping):
                source = cast(Mapping[K, V], other).items()
            elif hasattr(other, "keys"):
                key_source = cast(KeySource[K, V], other)
                source = ((key, key_source[key]) for key in key_source.keys())
            else:
                source = cast(Iterable[tuple[K, V]], other)
            incoming: dict[K, V] = {}
            for key, value in source:
                checked = cast(K, self._root.hash_input(key))
                incoming[checked] = value
            for key, value in cast(Mapping[K, V], kwargs).items():
                incoming[key] = value
            data.update(cast(dict[K, V], self._root.input_value(incoming)))

        self._change(apply)

    @overload
    def setdefault(self, key: K, default: None = None, /) -> V | None: ...
    @overload
    def setdefault(self, key: K, default: V, /) -> V: ...
    def setdefault(self, key: K, default: V | None = None, /) -> V | None:
        key = cast(K, self._root.hash_input(key))
        if key in self.read_payload():
            return self[key]
        self._change(lambda data: data.setdefault(key, cast(V, self._root.input_value(default))))
        return self[key]

    @overload
    def pop(self, key: K, /) -> V: ...
    @overload
    def pop(self, key: K, default: V, /) -> V: ...
    @overload
    def pop(self, key: K, default: D, /) -> V | D: ...
    def pop(self, key: K, *default: D) -> V | D:
        if len(default) > 1:
            raise TypeError(f"pop expected at most 2 arguments, got {len(default) + 1}")
        if default:
            return self._change(lambda data: data.pop(key, default[0]))
        return self._change(lambda data: data.pop(key))

    def popitem(self) -> tuple[K, V]:
        return self._change(lambda data: data.popitem())

    def clear(self) -> None:
        self._change(lambda data: data.clear())

    def __ior__(self, other: Mapping[K, V] | Iterable[tuple[K, V]]) -> Self:
        self.update(other)
        return self

    def __or__(self, other: dict[K, V] | OwnedDict[K, V]) -> dict[K, V]:
        return self.read_payload() | cast(dict[K, V], read(other))

    def __ror__(self, other: dict[K, V] | OwnedDict[K, V]) -> dict[K, V]:
        return cast(dict[K, V], read(other)) | self.read_payload()

    def copy(self) -> dict[K, V]:
        return dict(self.items())

    def __copy__(self) -> dict[K, V]:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, object] | None = None) -> dict[K, V]:
        return cast(dict[K, V], self._root.detached(self))

    @classmethod
    def fromkeys(cls, iterable: Iterable[K], value: D = cast(D, None)) -> dict[K, D]:
        return dict.fromkeys(iterable, value)


class OwnedSet(Owned[set[T]], MutableSet[T]):
    def __iter__(self) -> Iterator[T]:
        return self._iterate(self.read_payload())

    def add(self, value: T) -> None:
        self._change(lambda data: data.add(cast(T, self._root.hash_input(value))))

    def discard(self, value: T) -> None:
        self._change(lambda data: data.discard(value))

    def remove(self, value: T) -> None:
        self._change(lambda data: data.remove(value))

    def pop(self) -> T:
        return self._change(lambda data: data.pop())

    def clear(self) -> None:
        self._change(lambda data: data.clear())

    def update(self, *others: Iterable[T]) -> None:
        self._change(
            lambda data: data.update(
                *({cast(T, self._root.hash_input(value)) for value in other} for other in others)
            )
        )

    def intersection_update(self, *others: Iterable[T]) -> None:
        self._change(lambda data: data.intersection_update(*(set(o) for o in others)))

    def difference_update(self, *others: Iterable[T]) -> None:
        self._change(lambda data: data.difference_update(*(set(o) for o in others)))

    def symmetric_difference_update(self, other: Iterable[T]) -> None:
        self._change(
            lambda data: data.symmetric_difference_update(
                {cast(T, self._root.hash_input(value)) for value in other}
            )
        )

    def __ior__(self, other: Iterable[T]) -> Self:
        self.update(other)
        return self

    def __iand__(self, other: Iterable[T]) -> Self:
        self.intersection_update(other)
        return self

    def __isub__(self, other: Iterable[T]) -> Self:
        self.difference_update(other)
        return self

    def __ixor__(self, other: Iterable[T]) -> Self:
        self.symmetric_difference_update(other)
        return self

    def copy(self) -> set[T]:
        return set(self)

    def __copy__(self) -> set[T]:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, object] | None = None) -> set[T]:
        return self.copy()

    def union(self, *others: Iterable[T]) -> set[T]:
        return self.read_payload().union(*(o for o in others))

    def intersection(self, *others: Iterable[T]) -> set[T]:
        return self.read_payload().intersection(*(o for o in others))

    def difference(self, *others: Iterable[T]) -> set[T]:
        return self.read_payload().difference(*(o for o in others))

    def symmetric_difference(self, other: Iterable[T]) -> set[T]:
        return self.read_payload().symmetric_difference(other)

    def isdisjoint(self, other: Iterable[T]) -> bool:
        return self.read_payload().isdisjoint(other)

    def issubset(self, other: Iterable[T]) -> bool:
        return self.read_payload().issubset(other)

    def issuperset(self, other: Iterable[T]) -> bool:
        return self.read_payload().issuperset(other)

    def __or__(self, other: AbstractSet[D]) -> set[T | D]:
        return self.read_payload() | set(other)

    def __and__(self, other: AbstractSet[object]) -> set[T]:
        return self.read_payload() & set(other)

    def __sub__(self, other: AbstractSet[object]) -> set[T]:
        return self.read_payload() - set(other)

    def __xor__(self, other: AbstractSet[D]) -> set[T | D]:
        return self.read_payload() ^ set(other)

    def __ror__(self, other: AbstractSet[D]) -> set[T | D]:
        return set(other) | self.read_payload()

    def __rand__(self, other: AbstractSet[object]) -> set[T]:
        return self.read_payload() & set(other)

    def __rsub__(self, other: AbstractSet[object]) -> set[object]:
        return set(other) - self.read_payload()

    def __rxor__(self, other: AbstractSet[D]) -> set[T | D]:
        return set(other) ^ self.read_payload()

    def __lt__(self, other: AbstractSet[object]) -> bool:
        return self.read_payload() < set(other)

    def __le__(self, other: AbstractSet[object]) -> bool:
        return self.read_payload() <= set(other)

    def __gt__(self, other: AbstractSet[object]) -> bool:
        return self.read_payload() > set(other)

    def __ge__(self, other: AbstractSet[object]) -> bool:
        return self.read_payload() >= set(other)
