"""Minimal inheritance/type experiment; NOT a Pydandict implementation."""

# pyright: strict
from collections.abc import Iterator, Mapping, MutableMapping
from typing import assert_type

from pydantic import BaseModel


class MappingProbe(BaseModel, MutableMapping[str, object]):
    """Only tests model identity and mapping read types. Writes are disabled."""

    x: int

    def __getitem__(self, key: str) -> object:
        if key != "x":
            raise KeyError(key)
        return self.x

    def __setitem__(self, key: str, value: object) -> None:
        raise NotImplementedError("This is a read/type probe, not a safe model")

    def __delitem__(self, key: str) -> None:
        raise NotImplementedError("This is a read/type probe, not a safe model")

    def __iter__(self) -> Iterator[str]:  # pyright: ignore[reportIncompatibleMethodOverride]
        # Deliberate: BaseModel iterates pairs, whereas Mapping must iterate keys.
        return iter(("x",))

    def __len__(self) -> int:
        return 1


probe = MappingProbe(x=1)
base: BaseModel = probe
mapping: Mapping[str, object] = probe
mutable: MutableMapping[str, object] = probe
assert_type(probe.x, int)
assert_type(probe["x"], object)
assert_type(iter(probe), Iterator[str])
