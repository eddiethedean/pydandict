"""Protect the required SOL-007 workloads without asserting timing ceilings."""

from tools import benchmark


def test_production_workload_shapes_and_operations_are_complete():
    workloads = benchmark.workloads()
    assert [workload.name for workload in workloads] == [
        "flat_10",
        "flat_100",
        "flat_1000",
        "flat_10000",
        "linear_1",
        "linear_5",
        "linear_20",
        "mixed_parent",
    ]
    common = {"key_read", "scalar_write", "nested_leaf", "copy", "python_dump", "json_dump"}
    for workload in workloads:
        operations = benchmark.operations(workload)
        required = common | (
            {"coupled_10field", "rejected_parent"} if workload.name == "mixed_parent" else set()
        )
        assert set(operations) == required
        assert workload.model.model_dump() == workload.expected
        if workload.name.startswith("linear_"):
            depth = workload.shape["depth"]
            assert workload.shape["models"] == depth
            assert workload.shape["sequences"] == depth
            assert workload.shape["scalar_leaves"] == 2 * depth


def test_mixed_parent_rejection_and_coupled_batch_have_verified_state():
    workload = benchmark.workloads()[-1]
    operations = benchmark.operations(workload)
    handle = workload.model["numbers"]
    for name in ("coupled_10field", "rejected_parent", "nested_leaf"):
        operation = operations[name]
        before = benchmark._root_calls
        result = operation.invoke()
        operation.verify(result)
        assert benchmark._root_calls - before == 1
        assert workload.model["numbers"] is handle
