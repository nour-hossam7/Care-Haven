from __future__ import annotations

import json
from io import BytesIO
from urllib.error import HTTPError

import pytest

from carehaven_ui.api_client.cases import (
    list_review_queue,
    update_evidence_verification,
    upload_evidence,
)
from carehaven_ui.api_client.client import ApiClient, ApiError


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode()


def test_evidence_upload_uses_multipart_and_preserves_auth(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse({"evidence_id": "EVIDENCE-1"})

    monkeypatch.setattr("carehaven_ui.api_client.client.urlopen", fake_urlopen)
    result = upload_evidence(
        ApiClient(base_url="http://api.test", token="token-1"), "CASE-1",
        ("photo.png", b"image-bytes", "image/png"), "Flood damage",
    )
    request = captured["request"]
    body = request.data

    assert result == {"evidence_id": "EVIDENCE-1"}
    assert request.full_url == "http://api.test/cases/CASE-1/evidence"
    assert request.get_header("Authorization") == "Bearer token-1"
    assert request.get_header("Content-type").startswith("multipart/form-data; boundary=")
    assert b'filename="photo.png"' in body
    assert b"Content-Type: image/png" in body
    assert b'name="description"' in body
    assert b"Flood damage" in body


@pytest.mark.parametrize("code", [400, 413, 500])
def test_upload_http_errors_become_safe_api_errors(monkeypatch, code):
    def fake_urlopen(request, timeout):
        raise HTTPError(request.full_url, code, "error", {}, BytesIO(b"{}"))

    monkeypatch.setattr("carehaven_ui.api_client.client.urlopen", fake_urlopen)
    with pytest.raises(ApiError):
        upload_evidence(
            ApiClient(base_url="http://api.test"), "CASE-1",
            ("photo.png", b"image-bytes", "image/png"),
        )


def test_json_requests_remain_json(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        return FakeResponse({"ok": True})

    monkeypatch.setattr("carehaven_ui.api_client.client.urlopen", fake_urlopen)
    assert ApiClient(base_url="http://api.test").post("/cases", {"country": "Egypt"}) == {"ok": True}
    assert captured["request"].get_header("Content-type") == "application/json"
    assert json.loads(captured["request"].data) == {"country": "Egypt"}


def test_review_client_methods_use_existing_client():
    class Client:
        def get(self, path):
            self.path = path
            return {"items": []}

        def patch(self, path, payload):
            self.patch_args = (path, payload)
            return {"verification_status": "approved"}

    client = Client()
    assert list_review_queue(client, page=2, page_size=5) == {"items": []}
    assert client.path == "/cases/evidence/review-queue?page=2&page_size=5"
    assert update_evidence_verification(client, "EVIDENCE-1", "approved") == {"verification_status": "approved"}
    assert client.patch_args == (
        "/cases/evidence/EVIDENCE-1/verification",
        {"verification_status": "approved"},
    )
