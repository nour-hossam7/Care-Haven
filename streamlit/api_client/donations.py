from typing import Any
from .client import ApiClient
def list_donations(client: ApiClient) -> list[dict[str, Any]]: return client.get("/donations")
def create_donation(client: ApiClient, payload: dict[str, Any]) -> dict[str, Any]: return client.post("/donations", payload)
def case_donations(client: ApiClient, case_id: str) -> list[dict[str, Any]]: return client.get(f"/cases/{case_id}/donations")
