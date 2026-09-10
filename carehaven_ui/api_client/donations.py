from typing import Any
from .client import ApiClient
def list_donations(client: ApiClient) -> dict[str, Any]: return client.get("/donations")
def create_donation(client: ApiClient, payload: dict[str, Any]) -> dict[str, Any]: return client.post("/donations", payload)
def case_donations(client: ApiClient, case_id: str) -> dict[str, Any]: return client.get(f"/cases/{case_id}/donations")
def my_donation_history(client: ApiClient) -> dict[str, Any]: return client.get("/donations/my-history")
def get_donation(client: ApiClient, donation_id: str) -> dict[str, Any]: return client.get(f"/donations/{donation_id}")
