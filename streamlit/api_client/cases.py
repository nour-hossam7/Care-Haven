from typing import Any
from urllib.parse import urlencode
from .client import ApiClient
def list_cases(
    client: ApiClient, *, page: int | None = None, page_size: int | None = None,
    assistance_category: str | None = None, country: str | None = None,
    governorate: str | None = None, city: str | None = None, priority: str | None = None,
    severity: str | None = None, urgency: str | None = None, status: str | None = None,
) -> dict[str, Any]:
    filters = {"page": page, "page_size": page_size, "assistance_category": assistance_category,
               "country": country, "governorate": governorate, "city": city, "priority": priority,
               "severity": severity, "urgency": urgency, "status": status}
    query = urlencode({key: value for key, value in filters.items() if value is not None})
    return client.get(f"/cases?{query}" if query else "/cases")
def get_case(client: ApiClient, case_id: str) -> dict[str, Any]: return client.get(f"/cases/{case_id}")
def create_case(client: ApiClient, payload: dict[str, Any]) -> dict[str, Any]: return client.post("/cases", payload)
def update_case(client: ApiClient, case_id: str, payload: dict[str, Any]) -> dict[str, Any]: return client.put(f"/cases/{case_id}", payload)
def update_case_status(client: ApiClient, case_id: str, status: str) -> dict[str, Any]: return client.patch(f"/cases/{case_id}/status", {"status": status})
