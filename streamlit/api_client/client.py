"""Small, testable HTTP client; pages never make raw HTTP calls."""
from __future__ import annotations

import json
import uuid
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from streamlit.config import settings


class ApiError(RuntimeError):
    """Safe error suitable for display in the frontend."""


class ApiClient:
    def __init__(
        self,
        base_url: str = settings.backend_base_url,
        token: str | None = None,
        timeout: float = settings.api_timeout_seconds,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def request(
        self,
        method: str,
        path: str,
        payload: Any | None = None,
        files: dict[str, Any] | None = None,
    ) -> Any:
        headers = {"Accept": "application/json"}

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        body = None

        if files is not None:
            boundary = f"----CareHavenBoundary{uuid.uuid4().hex}"
            headers["Content-Type"] = (
                f"multipart/form-data; boundary={boundary}"
            )

            parts: list[bytes] = []

            # Add normal multipart form fields.
            if payload is not None:
                for key, value in payload.items():
                    parts.append(
                        (
                            f"--{boundary}\r\n"
                            f'Content-Disposition: form-data; name="{key}"\r\n'
                            f"\r\n"
                            f"{value}\r\n"
                        ).encode("utf-8")
                    )

            # Add uploaded files.
            for field_name, file_data in files.items():
                filename, content, content_type = file_data

                parts.append(
                    (
                        f"--{boundary}\r\n"
                        f'Content-Disposition: form-data; '
                        f'name="{field_name}"; filename="{filename}"\r\n'
                        f"Content-Type: {content_type}\r\n"
                        f"\r\n"
                    ).encode("utf-8")
                    + content
                    + b"\r\n"
                )

            parts.append(f"--{boundary}--\r\n".encode("utf-8"))
            body = b"".join(parts)

        elif payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload).encode("utf-8")

        request = Request(
            f"{self.base_url}{path}",
            data=body,
            headers=headers,
            method=method.upper(),
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                content = response.read()

                if not content:
                    return None

                try:
                    return json.loads(content)
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    raise ApiError(
                        "The CareHaven backend returned an invalid response."
                    ) from exc

        except HTTPError as exc:
            messages = {
                400: "The request could not be processed.",
                401: (
                    "Your session is invalid or expired. "
                    "Please sign in again."
                ),
                403: "You do not have permission to perform this action.",
                404: "The requested resource was not found.",
                409: "This conflicts with existing data.",
                413: (
                    "The uploaded image is too large. "
                    "Maximum size is 10 MB."
                ),
                422: "Please check the submitted information.",
                500: (
                    "The CareHaven backend encountered an error. "
                    "Please try again later."
                ),
            }

            raise ApiError(
                messages.get(
                    exc.code,
                    "The request could not be completed.",
                )
            ) from exc

        except (URLError, TimeoutError, OSError) as exc:
            raise ApiError(
                "The CareHaven backend is unavailable. "
                "Please try again later."
            ) from exc

    def get(self, path: str) -> Any:
        return self.request("GET", path)

    def post(
        self,
        path: str,
        payload: Any | None = None,
    ) -> Any:
        return self.request("POST", path, payload)

    def put(
        self,
        path: str,
        payload: Any | None = None,
    ) -> Any:
        return self.request("PUT", path, payload)

    def delete(self, path: str) -> Any:
        return self.request("DELETE", path)

    def patch(
        self,
        path: str,
        payload: Any | None = None,
    ) -> Any:
        return self.request("PATCH", path, payload)