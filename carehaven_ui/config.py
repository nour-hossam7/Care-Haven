"""Environment-backed configuration for the Streamlit frontend."""
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    backend_base_url: str = os.getenv("CAREHAVEN_API_BASE_URL", "http://localhost:8000")
    api_timeout_seconds: float = float(os.getenv("CAREHAVEN_API_TIMEOUT", "15"))
    app_title: str = os.getenv("CAREHAVEN_APP_TITLE", "Care-Haven")
    max_upload_mb: int = int(os.getenv("CAREHAVEN_MAX_UPLOAD_MB", "10"))

settings = Settings()
