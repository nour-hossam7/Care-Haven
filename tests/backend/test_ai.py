from __future__ import annotations

from types import SimpleNamespace

import pytest
import requests
from fastapi import HTTPException
from fastapi.testclient import TestClient

from ai.llm.client import LLMResponseError, LLMTimeoutError, LLMUnavailableError, OllamaCaseAnalysisClient
from ai.llm.schemas import CaseAnalysisResult
from ai.priority.priority_engine import PriorityCalculationError, calculate_priority
from backend.services import ai_service
from backend.models.user import UserRole
from backend.main import app
from backend.schemas.ai import HybridAnalysisResponse, HybridPriorityResult


VALID_RESULT = {
    "category": "Emergency Aid", "assistance": ["Food", "Shelter"],
    "people_affected": 6, "severity": "High", "summary": "A family needs urgent support.",
}


class Response:
    def __init__(self, payload): self.payload = payload
    def raise_for_status(self): return None
    def json(self): return self.payload


class FakeSession:
    def __init__(self, case=None, fail_commit=False):
        self.case = case
        self.fail_commit = fail_commit
        self.added = None
        self.commits = 0
        self.rollbacks = 0

    def get(self, _, case_id):
        return self.case if self.case and self.case.case_id == case_id else None

    def add(self, value): self.added = value

    def commit(self):
        self.commits += 1
        if self.fail_commit:
            raise RuntimeError("database unavailable")

    def refresh(self, value):
        value.id = 99

    def rollback(self): self.rollbacks += 1


def hybrid_case(created_by="USER-1", **overrides):
    values = {
        "case_id": "CASE-1", "created_by": created_by, "description": "Family needs help",
        "assistance_category": "Medical Aid", "people_affected": 50, "country": "Egypt",
        "governorate": None, "city": None, "severity": "High", "urgency": "Critical",
        "required_resources": "Medical supplies", "estimated_funding": 1000, "current_funding": 0,
        "priority": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class GoodClient:
    def analyze(self, _): return CaseAnalysisResult(**VALID_RESULT)


def test_llm_client_validates_successful_structured_response(monkeypatch):
    monkeypatch.setattr("ai.llm.client.requests.post", lambda *_, **__: Response({"response": __import__("json").dumps(VALID_RESULT)}))
    assert OllamaCaseAnalysisClient().analyze({"description": "help"}) == CaseAnalysisResult(**VALID_RESULT)


@pytest.mark.parametrize("payload", [{"response": "not json"}, {"response": '{"category":"Food"}'}])
def test_llm_client_rejects_malformed_or_invalid_structured_output(monkeypatch, payload):
    monkeypatch.setattr("ai.llm.client.requests.post", lambda *_, **__: Response(payload))
    with pytest.raises(LLMResponseError):
        OllamaCaseAnalysisClient().analyze({"description": "help"})


def test_llm_client_maps_unavailable_and_timeout(monkeypatch):
    monkeypatch.setattr("ai.llm.client.requests.post", lambda *_, **__: (_ for _ in ()).throw(requests.ConnectionError()))
    with pytest.raises(LLMUnavailableError): OllamaCaseAnalysisClient().analyze({})
    monkeypatch.setattr("ai.llm.client.requests.post", lambda *_, **__: (_ for _ in ()).throw(requests.Timeout()))
    with pytest.raises(LLMTimeoutError): OllamaCaseAnalysisClient().analyze({})


def test_priority_reuses_existing_formula_and_is_deterministic():
    kwargs = dict(severity="High", urgency="Critical", people_affected=50, estimated_funding=1000, current_funding=0, assistance_category="Medical Aid")
    first = calculate_priority(**kwargs)
    assert first == calculate_priority(**kwargs)
    assert (first.score, first.priority_level) == (14, "Critical")


@pytest.mark.parametrize("kwargs", [
    dict(severity="Unknown", urgency="High", people_affected=1, estimated_funding=100, current_funding=0, assistance_category="Food"),
    dict(severity="Low", urgency="Low", people_affected=0, estimated_funding=100, current_funding=0, assistance_category="Food"),
    dict(severity="Low", urgency="Low", people_affected=1, estimated_funding=0, current_funding=0, assistance_category="Food"),
])
def test_priority_rejects_invalid_inputs(kwargs):
    with pytest.raises(PriorityCalculationError): calculate_priority(**kwargs)


def test_priority_boundary_labels():
    low = calculate_priority(severity="Low", urgency="Low", people_affected=1, estimated_funding=100, current_funding=100, assistance_category="Food")
    medium = calculate_priority(severity="High", urgency="High", people_affected=1, estimated_funding=100, current_funding=100, assistance_category="Food")
    high = calculate_priority(severity="Critical", urgency="Critical", people_affected=1, estimated_funding=100, current_funding=50, assistance_category="Food")
    assert low.priority_level == "Low"
    assert medium.priority_level == "Medium"
    assert high.priority_level == "High"


def test_ai_service_hides_llm_failure_from_api_callers(monkeypatch):
    case = SimpleNamespace(
        case_id="CASE-1", created_by="USER-1", description="Help", assistance_category="Food",
        people_affected=1, country="Egypt", governorate=None, city=None, severity="Low", urgency="Low",
        required_resources=None, estimated_funding=100, current_funding=0,
    )
    monkeypatch.setattr(ai_service, "get_case_or_404", lambda *_: case)
    monkeypatch.setattr(ai_service, "_assert_can_modify", lambda *_: None)
    class BadClient:
        def analyze(self, _): raise LLMUnavailableError("internal")
    with pytest.raises(HTTPException) as exc:
        ai_service.analyze_case(SimpleNamespace(), "CASE-1", SimpleNamespace(), BadClient())
    assert exc.value.status_code == 503


def test_hybrid_analysis_combines_available_llm_and_priority_and_persists():
    case = hybrid_case()
    db = FakeSession(case)
    user = SimpleNamespace(user_id="USER-1", role=UserRole.USER)

    analysis, llm, priority, unavailable = ai_service.run_hybrid_analysis(db, "CASE-1", user, GoodClient())

    assert analysis.id == 99
    assert analysis.analysis_type == "hybrid_case_analysis"
    assert llm == CaseAnalysisResult(**VALID_RESULT)
    assert priority and priority.priority_level == "Critical"
    assert case.priority == "Critical"
    assert unavailable == []
    assert db.commits == 1


def test_hybrid_analysis_allows_admin_access_to_another_users_case():
    db = FakeSession(hybrid_case(created_by="USER-OTHER"))
    admin = SimpleNamespace(user_id="ADMIN-1", role=UserRole.ADMIN)

    analysis, _, _, _ = ai_service.run_hybrid_analysis(db, "CASE-1", admin, GoodClient())

    assert analysis.id == 99


def test_hybrid_analysis_rejects_other_users_case():
    db = FakeSession(hybrid_case(created_by="USER-OTHER"))
    user = SimpleNamespace(user_id="USER-1", role=UserRole.USER)

    with pytest.raises(HTTPException) as exc:
        ai_service.run_hybrid_analysis(db, "CASE-1", user, GoodClient())

    assert exc.value.status_code == 403


def test_hybrid_analysis_missing_case_is_404():
    with pytest.raises(HTTPException) as exc:
        ai_service.run_hybrid_analysis(FakeSession(), "CASE-MISSING", SimpleNamespace(), GoodClient())

    assert exc.value.status_code == 404


def test_hybrid_analysis_keeps_priority_when_llm_fails():
    class FailingClient:
        def analyze(self, _): raise LLMUnavailableError("unavailable")

    _, llm, priority, unavailable = ai_service.run_hybrid_analysis(
        FakeSession(hybrid_case()), "CASE-1", SimpleNamespace(user_id="USER-1", role=UserRole.USER), FailingClient()
    )

    assert llm is None
    assert priority is not None
    assert unavailable == ["LLM analysis is temporarily unavailable"]


def test_hybrid_analysis_keeps_llm_when_priority_cannot_be_calculated():
    case = hybrid_case(estimated_funding=None)

    _, llm, priority, unavailable = ai_service.run_hybrid_analysis(
        FakeSession(case), "CASE-1", SimpleNamespace(user_id="USER-1", role=UserRole.USER), GoodClient()
    )

    assert llm is not None
    assert priority is None
    assert unavailable == ["Priority calculation could not be completed"]


def test_hybrid_analysis_rejects_invalid_client_result_without_losing_priority():
    class InvalidClient:
        def analyze(self, _): return {"unexpected": "shape"}

    _, llm, priority, unavailable = ai_service.run_hybrid_analysis(
        FakeSession(hybrid_case()), "CASE-1", SimpleNamespace(user_id="USER-1", role=UserRole.USER), InvalidClient()
    )

    assert llm is None
    assert priority is not None
    assert unavailable == ["LLM analysis returned an invalid response"]


def test_hybrid_analysis_rolls_back_if_persistence_fails():
    db = FakeSession(hybrid_case(), fail_commit=True)

    with pytest.raises(HTTPException) as exc:
        ai_service.run_hybrid_analysis(
            db, "CASE-1", SimpleNamespace(user_id="USER-1", role=UserRole.USER), GoodClient()
        )

    assert exc.value.status_code == 500
    assert db.rollbacks == 1


def test_hybrid_response_schema_accepts_available_components():
    response = HybridAnalysisResponse(
        analysis_id=99,
        case_id="CASE-1",
        llm_analysis=CaseAnalysisResult(**VALID_RESULT),
        priority=HybridPriorityResult(score=14, priority_level="Critical", reasons=["Severity: High"]),
        unavailable_components=[],
    )

    assert response.model_dump()["priority"]["priority_level"] == "Critical"


def test_hybrid_endpoint_requires_authentication():
    response = TestClient(app).post("/ai/cases/CASE-1/hybrid-analysis")

    assert response.status_code == 401
