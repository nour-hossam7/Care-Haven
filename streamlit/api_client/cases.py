from typing import Any
from .client import ApiClient
def list_cases(client: ApiClient) -> list[dict[str, Any]]: return client.get("/cases")
def get_case(client: ApiClient, case_id: str) -> dict[str, Any]: return client.get(f"/cases/{case_id}")
def create_case(client: ApiClient, payload: dict[str, Any]) -> dict[str, Any]: return client.post("/cases", payload)
def update_case(client: ApiClient, case_id: str, payload: dict[str, Any]) -> dict[str, Any]: return client.put(f"/cases/{case_id}", payload)
