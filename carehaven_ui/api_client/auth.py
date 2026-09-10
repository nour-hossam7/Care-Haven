from typing import Any
from .client import ApiClient
def register(client: ApiClient, email: str, password: str) -> dict[str, Any]: return client.post("/auth/register", {"email": email, "password": password})
def login(client: ApiClient, email: str, password: str) -> dict[str, Any]: return client.post("/auth/login", {"email": email, "password": password})
def current_user(client: ApiClient) -> dict[str, Any]: return client.get("/auth/me")
