"""Private protocol handles with one authoritative payload per owned node.

Concrete built-in subclasses were rejected: C consumers can bypass their overrides
and silently read an unused base buffer. These ABC guards have no such buffer.
The model serializer delegates with a raw snapshot so field serializers still work.
"""

from __future__ import annotations

from typing import Any, Callable
from collections.abc import MutableMapping, MutableSequence, MutableSet


class Owned:
    _data: Any
    _root: Any
    _alive: bool
    _path: tuple[Any, ...]
    _version: int

    def _check(self) -> None:
        if not self._alive:
            raise RuntimeError("stale owned handle")

    def _read(self) -> Any:
        self._check()
        return self._data

    def _change(self, operation: Callable[[Any], Any]) -> Any:
        self._check()
        return self._root._container_change(self, operation)

    def _iterate(self, values: Any):
        self._check()
        version = self._version
        iterator = iter(values)

        def generate():
            while True:
                self._check()
                if self._version != version:
                    raise RuntimeError("owned container changed during iteration")
                try:
                    item = next(iterator)
                except StopIteration:
                    return
                yield item

        return generate()

    def __len__(self):
        return len(self._read())

    def __repr__(self):
        return repr(self._read())

    def __str__(self):
        return str(self._read())

    def __contains__(self, value):
        return value in self._read()

    def __eq__(self, other):
        return self._read() == read(other)

    def __ne__(self, other):
        return self._read() != read(other)


def read(value):
    return value._read() if isinstance(value, Owned) else value


class OwnedList(Owned, MutableSequence[Any]):
    def __iter__(self):
        return self._iterate(self._read())

    def __reversed__(self):
        return self._iterate(reversed(self._read()))

    def __getitem__(self, key):
        return self._read()[key]

    def __setitem__(self, key, value):
        if (
            not isinstance(key, slice)
            and self._read()[key] is value
            and isinstance(value, Owned)
        ):
            value._check()
            return
        self._change(
            lambda data: data.__setitem__(
                key, self._root._input(list(value) if isinstance(key, slice) else value)
            )
        )

    def __delitem__(self, key):
        self._change(lambda data: data.__delitem__(key))

    def append(self, value):
        self._change(lambda data: data.append(self._root._input(value)))

    def extend(self, values):
        self._change(lambda data: data.extend(self._root._input(list(values))))

    def insert(self, index, value):
        self._change(lambda data: data.insert(index, self._root._input(value)))

    def pop(self, index=-1):
        return self._change(lambda data: data.pop(index))

    def remove(self, value):
        self._change(lambda data: data.remove(value))

    def clear(self):
        self._change(lambda data: data.clear())

    def reverse(self):
        self._change(lambda data: data.reverse())

    def sort(self, *, key=None, reverse=False):
        self._change(lambda data: data.sort(key=key, reverse=reverse))

    def __iadd__(self, values):
        self.extend(values)
        return self

    def __imul__(self, count):
        # Repeated mutable elements must be independently owned, not aliased.
        def multiply(data):
            original = list(data)
            data *= count
            if count > 1:
                data[len(original) :] = [
                    self._root._input(v) for v in data[len(original) :]
                ]

        self._change(multiply)
        return self

    def copy(self):
        return list(self)

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, memo):
        return self._root._input(self)

    def count(self, value):
        return self._read().count(value)

    def index(self, value, *args):
        return self._read().index(value, *args)

    def __add__(self, other):
        return self._read() + read(other)

    def __radd__(self, other):
        return read(other) + self._read()

    def __mul__(self, count):
        return self._read() * count

    def __rmul__(self, count):
        return self * count

    def __lt__(self, other):
        return self._read() < read(other)

    def __le__(self, other):
        return self._read() <= read(other)

    def __gt__(self, other):
        return self._read() > read(other)

    def __ge__(self, other):
        return self._read() >= read(other)


class OwnedDict(Owned, MutableMapping[Any, Any]):
    def __iter__(self):
        return self._iterate(self._read())

    def __reversed__(self):
        return self._iterate(reversed(self._read()))

    def __getitem__(self, key):
        return self._read()[key]

    def __setitem__(self, key, value):
        if (
            key in self._read()
            and self._read()[key] is value
            and isinstance(value, Owned)
        ):
            value._check()
            return
        self._change(lambda data: data.__setitem__(key, self._root._input(value)))

    def __delitem__(self, key):
        self._change(lambda data: data.__delitem__(key))

    def get(self, key, default=None):
        return self._read().get(key, default)

    def keys(self):
        from collections.abc import KeysView

        return KeysView(self)

    def values(self):
        from collections.abc import ValuesView

        return ValuesView(self)

    def items(self):
        from collections.abc import ItemsView

        return ItemsView(self)

    def update(self, other=(), /, **kwargs):
        self._change(lambda data: data.update(self._root._input(dict(other, **kwargs))))

    def setdefault(self, key, default=None):
        if key in self._read():
            return self[key]
        self._change(lambda data: data.setdefault(key, self._root._input(default)))
        return self[key]

    def pop(self, key, *default):
        return self._change(lambda data: data.pop(key, *default))

    def popitem(self):
        return self._change(lambda data: data.popitem())

    def clear(self):
        self._change(lambda data: data.clear())

    def __ior__(self, other):
        self.update(other)
        return self

    def __or__(self, other):
        return self._read() | read(other)

    def __ror__(self, other):
        return read(other) | self._read()

    def copy(self):
        return dict(self.items())

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, memo):
        return self._root._input(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        return dict.fromkeys(iterable, value)


class OwnedSet(Owned, MutableSet[Any]):
    def __iter__(self):
        return self._iterate(self._read())

    def add(self, value):
        self._change(lambda data: data.add(self._root._input(value)))

    def discard(self, value):
        self._change(lambda data: data.discard(value))

    def remove(self, value):
        self._change(lambda data: data.remove(value))

    def pop(self):
        return self._change(lambda data: data.pop())

    def clear(self):
        self._change(lambda data: data.clear())

    def update(self, *others):
        self._change(
            lambda data: data.update(*(self._root._input(set(o)) for o in others))
        )

    def intersection_update(self, *others):
        self._change(lambda data: data.intersection_update(*(set(o) for o in others)))

    def difference_update(self, *others):
        self._change(lambda data: data.difference_update(*(set(o) for o in others)))

    def symmetric_difference_update(self, other):
        self._change(
            lambda data: data.symmetric_difference_update(self._root._input(set(other)))
        )

    def __ior__(self, other):
        self.update(other)
        return self

    def __iand__(self, other):
        self.intersection_update(other)
        return self

    def __isub__(self, other):
        self.difference_update(other)
        return self

    def __ixor__(self, other):
        self.symmetric_difference_update(other)
        return self

    def copy(self):
        return set(self)

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, memo):
        return self.copy()

    def union(self, *others):
        return self._read().union(*(read(o) for o in others))

    def intersection(self, *others):
        return self._read().intersection(*(read(o) for o in others))

    def difference(self, *others):
        return self._read().difference(*(read(o) for o in others))

    def symmetric_difference(self, other):
        return self._read().symmetric_difference(read(other))

    def isdisjoint(self, other):
        return self._read().isdisjoint(read(other))

    def issubset(self, other):
        return self._read().issubset(read(other))

    def issuperset(self, other):
        return self._read().issuperset(read(other))

    def __or__(self, other):
        return self._read() | read(other)

    def __and__(self, other):
        return self._read() & read(other)

    def __sub__(self, other):
        return self._read() - read(other)

    def __xor__(self, other):
        return self._read() ^ read(other)

    def __ror__(self, other):
        return read(other) | self._read()

    def __rand__(self, other):
        return read(other) & self._read()

    def __rsub__(self, other):
        return read(other) - self._read()

    def __rxor__(self, other):
        return read(other) ^ self._read()

    def __lt__(self, other):
        return self._read() < read(other)

    def __le__(self, other):
        return self._read() <= read(other)

    def __gt__(self, other):
        return self._read() > read(other)

    def __ge__(self, other):
        return self._read() >= read(other)
