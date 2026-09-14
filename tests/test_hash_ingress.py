"""SOL-002 must reject model members before invoking native hashing."""

from collections.abc import MutableMapping, MutableSet

import pytest

from pydandict import DictModel


@pytest.mark.parametrize("operation", ["mapping_set", "set_add", "set_update"])
def test_unhashable_model_members_get_the_ownership_diagnostic(operation):
    class Member(DictModel):
        value: int

    class Root(DictModel):
        table: MutableMapping[object, int]
        flags: MutableSet[object]

    model = Root(table={}, flags=set())
    member = Member(value=1)
    table, flags = model.table, model.flags
    before = model.model_dump_json(), model.model_fields_set
    with pytest.raises(TypeError, match=r"^pydandict_unsupported_value:"):
        if operation == "mapping_set":
            table[member] = 1
        elif operation == "set_add":
            flags.add(member)
        else:
            flags.update(value for value in [member])
    assert (model.model_dump_json(), model.model_fields_set) == before
    assert model.table is table and model.flags is flags
    table["valid"] = 1
    flags.add(2)
    assert model.model_dump() == {"table": {"valid": 1}, "flags": {2}}
