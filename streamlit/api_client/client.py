"""Small, testable HTTP client; pages never make raw HTTP calls."""
from __future__ import annotations
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from streamlit.config import settings

class ApiError(RuntimeError):
    """Safe error suitable for display in the frontend."""

class ApiClient:
    def __init__(self, base_url: str = settings.backend_base_url, token: str | None = None, timeout: float = settings.api_timeout_seconds) -> None:
        self.base_url, self.token, self.timeout = base_url.rstrip("/"), token, timeout
    def request(self, method: str, path: str, payload: Any | None = None, files: dict[str, Any] | None = None) -> Any:
        if files is not None:
            raise ApiError("File uploads need backend multipart-contract integration, which is unavailable in this repository.")
        headers = {"Accept": "application/json"}
        if self.token: headers["Authorization"] = f"Bearer {self.token}"
        body = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload).encode("utf-8")
        request = Request(f"{self.base_url}{path}", data=body, headers=headers, method=method.upper())
        try:
            with urlopen(request, timeout=self.timeout) as response:
                content = response.read()
                if not content:
                    return None
                try:
                    return json.loads(content)
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    raise ApiError("The CareHaven backend returned an invalid response.") from exc
        except HTTPError as exc:
            messages = {
                400: "The request could not be processed.",
                401: "Your session is invalid or expired. Please sign in again.",
                403: "You do not have permission to perform this action.",
                404: "The requested resource was not found.",
                409: "This conflicts with existing data.",
                422: "Please check the submitted information.",
                500: "The CareHaven backend encountered an error. Please try again later.",
            }
            raise ApiError(messages.get(exc.code, "The request could not be completed.")) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise ApiError("The CareHaven backend is unavailable. Please try again later.") from exc
    def get(self, path: str) -> Any: return self.request("GET", path)
    def post(self, path: str, payload: Any | None = None) -> Any: return self.request("POST", path, payload)
    def put(self, path: str, payload: Any | None = None) -> Any: return self.request("PUT", path, payload)
    def delete(self, path: str) -> Any: return self.request("DELETE", path)
    def patch(self, path: str, payload: Any | None = None) -> Any: return self.request("PATCH", path, payload)
