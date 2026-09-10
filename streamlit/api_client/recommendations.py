from typing import Any
from .client import ApiClient
def recommendations_for(client: ApiClient, donor_id: str) -> list[dict[str, Any]]: return client.get(f"/recommendations/{donor_id}")
