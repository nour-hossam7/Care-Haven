from typing import Any
from .client import ApiClient
def ask(client: ApiClient, question: str) -> dict[str, Any]: return client.post("/chat", {"question": question})
