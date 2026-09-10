"""Vercel ASGI entrypoint for the existing Care-Haven FastAPI application."""

from backend.main import app

__all__ = ["app"]
