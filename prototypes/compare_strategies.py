"""Controls for the candidate engine and the upstream alias-wrap limitation."""

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


def run():
    class Coupled(BaseModel):
        model_config = ConfigDict(validate_assignment=True)
        left: int
        right: int

        @model_validator(mode="after")
        def equal(self):
            if self.left != self.right:
                raise ValueError("must agree")
            return self

    live = Coupled(left=1, right=1)
    failed_orders = []
    for first in ("left", "right"):
        candidate = live.model_copy()
        try:
            setattr(candidate, first, 2)
        except ValidationError:
            failed_orders.append(first)
    assert failed_orders == ["left", "right"]
    full = Coupled.model_validate({"left": 2, "right": 2})
    assert full.left == full.right == 2 and live.left == live.right == 1

    class WrappedAlias(BaseModel):
        n: int = Field(default=1, alias="number")

        @model_validator(mode="wrap")
        @classmethod
        def passthrough(cls, value, handler):
            return handler(value)

    # Record, rather than hide, why a canonical core-schema adapter is needed.
    result = WrappedAlias.model_validate({"n": 2}, by_name=True, by_alias=False)
    return {
        "sequential_assignment_failed_first_keys": failed_orders,
        "full_candidate_coupled_update": full.model_dump(),
        "original_preserved": live.model_dump(),
        "upstream_wrapped_alias_by_name_requested": 2,
        "upstream_wrapped_alias_by_name_observed": result.n,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run(), indent=2))
