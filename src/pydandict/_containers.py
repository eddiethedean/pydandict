"""Private protocol handles with one authoritative payload per owned node.

Concrete built-in subclasses were rejected: C consumers can bypass their overrides
and silently read an unused base buffer. These ABC guards have no such buffer.
The model serializer delegates with a raw snapshot so field serializers still work.
"""

from __future__ import annotations

from collections.abc import MutableMapping, MutableSequence, MutableSet
from typing import Any, Callable, Self


class Owned:
    _data: Any
    _root: Any
    _alive: bool
    _path: tuple[Any, ...]
    _version: int

    def _check(self) -> None:
        if not self._alive:
            raise RuntimeError("pydandict_stale_handle: stale owned handle")

    def _read(self) -> Any:
        self._check()
        return self._data

    def _change(self, operation: Callable[[Any], Any]) -> Any:
        self._check()
        return self._root._container_change(self, operation)

    def _iterate(self, values: Any) -> Any:
        self._check()
        version = self._version
        iterator = iter(values)

        def generate() -> Any:
            while True:
                self._check()
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
        return len(self._read())

    def __repr__(self) -> str:
        return repr(self._read())

    def __str__(self) -> str:
        return str(self._read())

    def __contains__(self, value: object) -> bool:
        return value in self._read()

    def __eq__(self, other: object) -> bool:
        return self._read() == read(other)

    def __ne__(self, other: object) -> bool:
        return self._read() != read(other)


def read(value: Any) -> Any:
    return value._read() if isinstance(value, Owned) else value  # pyright: ignore[reportPrivateUsage]


class OwnedList(Owned, MutableSequence[Any]):
    def __iter__(self) -> Any:
        return self._iterate(self._read())

    def __reversed__(self) -> Any:
        return self._iterate(reversed(self._read()))

    def __getitem__(self, key: int | slice) -> Any:
        return self._read()[key]

    def __setitem__(self, key: int | slice, value: Any) -> None:
        if (
            not isinstance(key, slice)
            and self._read()[key] is value
            and isinstance(value, (Owned,))
        ):
            value._check()
            self._root._identity_handle_write(value)
            return
        self._change(
            lambda data: data.__setitem__(
                key, self._root._input(list(value) if isinstance(key, slice) else value)
            )
        )

    def __delitem__(self, key: int | slice) -> None:
        self._change(lambda data: data.__delitem__(key))

    def append(self, value: Any) -> None:
        self._change(lambda data: data.append(self._root._input(value)))

    def extend(self, values: Any) -> None:
        self._change(lambda data: data.extend(self._root._input(list(values))))

    def insert(self, index: int, value: Any) -> None:
        self._change(lambda data: data.insert(index, self._root._input(value)))

    def pop(self, index: int = -1) -> Any:
        return self._change(lambda data: data.pop(index))

    def remove(self, value: Any) -> None:
        self._change(lambda data: data.remove(value))

    def clear(self) -> None:
        self._change(lambda data: data.clear())

    def reverse(self) -> None:
        self._change(lambda data: data.reverse())

    def sort(self, *, key: Any = None, reverse: bool = False) -> None:
        self._change(lambda data: data.sort(key=key, reverse=reverse))

    def __iadd__(self, values: Any) -> Self:
        self.extend(values)
        return self

    def __imul__(self, count: int) -> Self:
        # Repeated mutable elements must be independently owned, not aliased.
        def multiply(data: list[Any]) -> None:
            original = list(data)
            data *= count
            if count > 1:
                data[len(original) :] = [self._root._input(v) for v in data[len(original) :]]

        self._change(multiply)
        return self

    def copy(self) -> list[Any]:
        return list(self)

    def __copy__(self) -> list[Any]:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any] | None = None) -> list[Any]:
        return self._root._detached(self)

    def count(self, value: Any) -> int:
        return self._read().count(value)

    def index(self, value: Any, *args: Any) -> int:
        return self._read().index(value, *args)

    def __add__(self, other: Any) -> Any:
        return self._read() + read(other)

    def __radd__(self, other: Any) -> Any:
        return read(other) + self._read()

    def __mul__(self, count: int) -> Any:
        return self._read() * count

    def __rmul__(self, count: int) -> Any:
        return self * count

    def __lt__(self, other: Any) -> bool:
        return self._read() < read(other)

    def __le__(self, other: Any) -> bool:
        return self._read() <= read(other)

    def __gt__(self, other: Any) -> bool:
        return self._read() > read(other)

    def __ge__(self, other: Any) -> bool:
        return self._read() >= read(other)


class OwnedDict(Owned, MutableMapping[Any, Any]):
    def __iter__(self) -> Any:
        return self._iterate(self._read())

    def __reversed__(self) -> Any:
        return self._iterate(reversed(self._read()))

    def __getitem__(self, key: Any) -> Any:
        return self._read()[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        if key in self._read() and self._read()[key] is value and isinstance(value, Owned):
            value._check()
            self._root._identity_handle_write(value)
            return
        self._change(lambda data: data.__setitem__(key, self._root._input(value)))

    def __delitem__(self, key: Any) -> None:
        self._change(lambda data: data.__delitem__(key))

    def get(self, key: Any, default: Any = None) -> Any:
        return self._read().get(key, default)

    def keys(self) -> Any:
        from collections.abc import KeysView

        return KeysView(self)

    def values(self) -> Any:
        from collections.abc import ValuesView

        return ValuesView(self)

    def items(self) -> Any:
        from collections.abc import ItemsView

        return ItemsView(self)

    def update(self, other: Any = (), /, **kwargs: Any) -> None:
        self._change(lambda data: data.update(self._root._input(dict(other, **kwargs))))

    def setdefault(self, key: Any, default: Any = None) -> Any:
        if key in self._read():
            return self[key]
        self._change(lambda data: data.setdefault(key, self._root._input(default)))
        return self[key]

    def pop(self, key: Any, *default: Any) -> Any:
        return self._change(lambda data: data.pop(key, *default))

    def popitem(self) -> tuple[Any, Any]:
        return self._change(lambda data: data.popitem())

    def clear(self) -> None:
        self._change(lambda data: data.clear())

    def __ior__(self, other: Any) -> Self:
        self.update(other)
        return self

    def __or__(self, other: Any) -> dict[Any, Any]:
        return self._read() | read(other)

    def __ror__(self, other: Any) -> dict[Any, Any]:
        return read(other) | self._read()

    def copy(self) -> dict[Any, Any]:
        return dict(self.items())

    def __copy__(self) -> dict[Any, Any]:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any] | None = None) -> dict[Any, Any]:
        return self._root._detached(self)

    @classmethod
    def fromkeys(cls, iterable: Any, value: Any = None) -> dict[Any, Any]:
        return dict.fromkeys(iterable, value)


class OwnedSet(Owned, MutableSet[Any]):
    def __iter__(self) -> Any:
        return self._iterate(self._read())

    def add(self, value: Any) -> None:
        self._change(lambda data: data.add(self._root._input(value)))

    def discard(self, value: Any) -> None:
        self._change(lambda data: data.discard(value))

    def remove(self, value: Any) -> None:
        self._change(lambda data: data.remove(value))

    def pop(self) -> Any:
        return self._change(lambda data: data.pop())

    def clear(self) -> None:
        self._change(lambda data: data.clear())

    def update(self, *others: Any) -> None:
        self._change(lambda data: data.update(*(self._root._input(set(o)) for o in others)))

    def intersection_update(self, *others: Any) -> None:
        self._change(lambda data: data.intersection_update(*(set(o) for o in others)))

    def difference_update(self, *others: Any) -> None:
        self._change(lambda data: data.difference_update(*(set(o) for o in others)))

    def symmetric_difference_update(self, other: Any) -> None:
        self._change(lambda data: data.symmetric_difference_update(self._root._input(set(other))))

    def __ior__(self, other: Any) -> Self:
        self.update(other)
        return self

    def __iand__(self, other: Any) -> Self:
        self.intersection_update(other)
        return self

    def __isub__(self, other: Any) -> Self:
        self.difference_update(other)
        return self

    def __ixor__(self, other: Any) -> Self:
        self.symmetric_difference_update(other)
        return self

    def copy(self) -> set[Any]:
        return set(self)

    def __copy__(self) -> set[Any]:
        return self.copy()

    def __deepcopy__(self, memo: dict[int, Any] | None = None) -> set[Any]:
        return self.copy()

    def union(self, *others: Any) -> set[Any]:
        return self._read().union(*(read(o) for o in others))

    def intersection(self, *others: Any) -> set[Any]:
        return self._read().intersection(*(read(o) for o in others))

    def difference(self, *others: Any) -> set[Any]:
        return self._read().difference(*(read(o) for o in others))

    def symmetric_difference(self, other: Any) -> set[Any]:
        return self._read().symmetric_difference(read(other))

    def isdisjoint(self, other: Any) -> bool:
        return self._read().isdisjoint(read(other))

    def issubset(self, other: Any) -> bool:
        return self._read().issubset(read(other))

    def issuperset(self, other: Any) -> bool:
        return self._read().issuperset(read(other))

    def __or__(self, other: Any) -> set[Any]:
        return self._read() | read(other)

    def __and__(self, other: Any) -> set[Any]:
        return self._read() & read(other)

    def __sub__(self, other: Any) -> set[Any]:
        return self._read() - read(other)

    def __xor__(self, other: Any) -> set[Any]:
        return self._read() ^ read(other)

    def __ror__(self, other: Any) -> set[Any]:
        return read(other) | self._read()

    def __rand__(self, other: Any) -> set[Any]:
        return read(other) & self._read()

    def __rsub__(self, other: Any) -> set[Any]:
        return read(other) - self._read()

    def __rxor__(self, other: Any) -> set[Any]:
        return read(other) ^ self._read()

    def __lt__(self, other: Any) -> bool:
        return self._read() < read(other)

    def __le__(self, other: Any) -> bool:
        return self._read() <= read(other)

    def __gt__(self, other: Any) -> bool:
        return self._read() > read(other)

    def __ge__(self, other: Any) -> bool:
        return self._read() >= read(other)
