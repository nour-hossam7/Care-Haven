from typing import Any
from .client import ApiClient
def analyze_image(client: ApiClient, payload: dict[str, Any]) -> dict[str, Any]: return client.post("/ai/analyze-image", payload)
def check_similarity(client: ApiClient, payload: dict[str, Any]) -> dict[str, Any]: return client.post("/ai/check-similarity", payload)
