from io import BytesIO
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, UploadFile

from backend.services.evidence_service import upload_case_evidence
from backend.services import evidence_service


def test_upload_rejects_unsupported_content_type():
    file = UploadFile(
        filename="document.txt",
        file=BytesIO(b"not an image"),
        headers={"content-type": "text/plain"},
    )

    case = SimpleNamespace(case_id="CASE-TEST")

    with pytest.raises(HTTPException) as exc_info:
        upload_case_evidence(
            db=None,
            case=case,
            file=file,
        )

    assert exc_info.value.status_code == 400
    assert "Unsupported image format" in exc_info.value.detail


def test_upload_rejects_poor_quality_image(monkeypatch):
    from PIL import Image

    image = Image.new("RGB", (100, 100), color="white")
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)

    file = UploadFile(
        filename="poor_quality.jpg",
        file=buffer,
        headers={"content-type": "image/jpeg"},
    )

    case = SimpleNamespace(case_id="CASE-TEST")

    monkeypatch.setattr(
        "backend.services.evidence_service.assess_image_quality",
        lambda _: {
            "is_acceptable": False,
            "quality_score": 0.25,
            "issues": ["Image resolution is too low"],
        },
    )

    with pytest.raises(HTTPException) as exc_info:
        upload_case_evidence(
            db=None,
            case=case,
            file=file,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["message"] == "Image quality is not acceptable."



def test_upload_saves_image_and_creates_evidence(tmp_path, monkeypatch):
    from pathlib import Path

    from backend.services import evidence_service

    image_path = Path("tests/backend/test_upload.png")
    image_bytes = image_path.read_bytes()

    file = UploadFile(
        filename="test_upload.png",
        file=BytesIO(image_bytes),
        headers={"content-type": "image/png"},
    )

    case = SimpleNamespace(case_id="CASE-TEST")

    class FakeSession:
        def __init__(self):
            self.added = None
            self.commits = 0

        def add(self, value):
            self.added = value

        def commit(self):
            self.commits += 1

        def refresh(self, value):
            return None

        def rollback(self):
            raise AssertionError("Rollback should not be called")

    db = FakeSession()

    monkeypatch.setattr(evidence_service, "UPLOAD_DIR", tmp_path)
    monkeypatch.setattr(
        evidence_service,
        "assess_image_quality",
        lambda _: {
            "is_acceptable": True,
            "quality_score": 1.0,
            "issues": [],
        },
    )

    evidence = evidence_service.upload_case_evidence(
        db=db,
        case=case,
        file=file,
        description="Test evidence",
    )

    assert evidence.case_id == "CASE-TEST"
    assert evidence.evidence_type == "image"
    assert evidence.source_type == "user_upload"
    assert evidence.verification_status == "unreviewed"
    assert evidence.description == "Test evidence"
    assert db.commits == 1
    assert db.added is evidence

    saved_file = tmp_path / "CASE-TEST" / f"{evidence.evidence_id}.png"
    assert saved_file.is_file()
    assert saved_file.read_bytes() == image_bytes


def test_upload_endpoint_rejects_unauthorized_user(monkeypatch):
    from fastapi.testclient import TestClient

    from backend.main import app
    from backend.routers import evidence as evidence_router
    from backend.core.security import get_current_user

    case = SimpleNamespace(
        case_id="CASE-TEST",
        created_by="OWNER-1",
    )

    current_user = SimpleNamespace(
        user_id="OTHER-USER",
        role="user",
    )

    monkeypatch.setattr(
        evidence_router,
        "get_case_or_404",
        lambda db, case_id: case,
    )

    app.dependency_overrides[get_current_user] = lambda: current_user

    try:
        response = TestClient(app).post(
            "/cases/CASE-TEST/evidence",
            files={
                "file": (
                    "test.png",
                    b"fake image",
                    "image/png",
                )
            },
        )

        assert response.status_code == 403
        assert response.json()["detail"] == (
            "Not authorized to upload evidence for this case"
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)


class FakeEvidenceSession:
    def __init__(self, evidence=None):
        self.evidence = evidence
        self.commits = 0

    def get(self, model, evidence_id):
        if self.evidence and self.evidence.evidence_id == evidence_id:
            return self.evidence
        return None

    def commit(self):
        self.commits += 1

    def refresh(self, value):
        return None

    def rollback(self):
        return None


def test_review_action_updates_only_verification_status():
    evidence = SimpleNamespace(
        evidence_id="EVIDENCE-1", case_id="CASE-1", file_path="image.png",
        description="Before", verification_status="unreviewed",
    )
    db = FakeEvidenceSession(evidence)

    updated = evidence_service.update_evidence_verification(
        db, "EVIDENCE-1", "approved"
    )

    assert updated.verification_status == "approved"
    assert updated.case_id == "CASE-1"
    assert updated.file_path == "image.png"
    assert updated.description == "Before"
    assert db.commits == 1


@pytest.mark.parametrize("decision", ["pending", "", "APPROVED"])
def test_review_action_rejects_invalid_status(decision):
    with pytest.raises(HTTPException) as exc_info:
        evidence_service.update_evidence_verification(
            FakeEvidenceSession(), "EVIDENCE-1", decision
        )
    assert exc_info.value.status_code == 422


def test_review_action_returns_404_for_unknown_evidence():
    with pytest.raises(HTTPException) as exc_info:
        evidence_service.update_evidence_verification(
            FakeEvidenceSession(), "EVIDENCE-MISSING", "rejected"
        )
    assert exc_info.value.status_code == 404


def test_review_queue_filters_for_unreviewed_evidence():
    class Result:
        def all(self):
            return [SimpleNamespace(evidence_id="EVIDENCE-1")]

    class QueueSession:
        def scalar(self, query):
            return 1

        def scalars(self, query):
            self.query = query
            return Result()

    db = QueueSession()
    items, total, pages = evidence_service.list_unreviewed_evidence(
        db, page=2, page_size=10
    )
    compiled = str(db.query.compile(compile_kwargs={"literal_binds": True}))

    assert [item.evidence_id for item in items] == ["EVIDENCE-1"]
    assert (total, pages) == (1, 1)
    assert "case_evidence_manifest.verification_status = 'unreviewed'" in compiled
    assert "LIMIT 10 OFFSET 10" in compiled


def test_review_queue_rejects_unauthenticated_access():
    from fastapi.testclient import TestClient
    from backend.main import app

    assert TestClient(app).get("/cases/evidence/review-queue").status_code in {401, 403}


def test_review_queue_rejects_normal_user(monkeypatch):
    from fastapi.testclient import TestClient
    from backend.main import app
    from backend.core.database import get_db
    from backend.core.security import get_current_user
    from backend.models.user import UserRole

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        user_id="USER-1", role=UserRole.USER
    )
    app.dependency_overrides[get_db] = lambda: FakeEvidenceSession()
    try:
        assert TestClient(app).get("/cases/evidence/review-queue").status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_case_evidence_returns_safe_image_url_without_file_path(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    from backend.core.database import get_db
    from backend.core.security import get_current_user
    from backend.main import app
    from backend.routers import evidence as evidence_router
    from backend.services import evidence_service

    image = tmp_path / "CASE-TEST" / "evidence.svg"
    image.parent.mkdir()
    image.write_text("<svg xmlns='http://www.w3.org/2000/svg'></svg>")
    monkeypatch.setattr(evidence_router, "EVIDENCE_IMAGE_ROOT", tmp_path)
    monkeypatch.setattr(evidence_service, "EVIDENCE_IMAGE_ROOT", tmp_path)
    evidence = SimpleNamespace(
        evidence_id="EVIDENCE-TEST",
        case_id="CASE-TEST",
        evidence_type="image",
        file_path=str(image),
        source_type="synthetic_demo",
        uploaded_at=None,
        description="Test image",
        verification_status="unreviewed",
    )

    class FakeSession:
        def scalars(self, query):
            return SimpleNamespace(all=lambda: [evidence])

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(user_id="USER-1")
    app.dependency_overrides[get_db] = lambda: FakeSession()
    try:
        client = TestClient(app)
        response = client.get("/cases/CASE-TEST/evidence")
        assert response.status_code == 200
        payload = response.json()[0]
        assert payload["file_path"] is None
        assert payload["image_url"].endswith("/cases/evidence/files/CASE-TEST/evidence.svg")
        assert client.get("/cases/evidence/files/../backend/main.py").status_code == 404
    finally:
        app.dependency_overrides.clear()
