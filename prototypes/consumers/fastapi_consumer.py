"""Standalone HTTP/schema consumer; imports no prototype internals."""

from collections.abc import MutableSequence
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import Field, model_validator
from pydandict_prototype import DictModel


class Record(DictModel):
    budget: int = Field(default=10, ge=0)
    costs: MutableSequence[int] = Field(default_factory=list)
    display_name: str = Field(default="example", alias="displayName")

    @model_validator(mode="after")
    def bounded(self):
        if sum(self.costs) > self.budget:
            raise ValueError("budget exceeded")
        return self


app = FastAPI()


@app.post("/records", response_model=Record)
def endpoint(record: Record) -> Record:
    record.costs.append(1)
    return record


def main():
    with TestClient(app) as client:
        response = client.post("/records", json={"costs": [1], "displayName": "demo"})
        assert response.status_code == 200, response.text
        assert response.json() == {"budget": 10, "costs": [1, 1], "displayName": "demo"}
        assert client.post("/records", json={"budget": -1}).status_code == 422
        schemas = client.get("/openapi.json").json()["components"]["schemas"]
        assert any(
            "costs" in schema.get("properties", {}) for schema in schemas.values()
        )
    print("FastAPI consumer: passed")


if __name__ == "__main__":
    main()
