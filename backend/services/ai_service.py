from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ai.llm.client import (
    LLMIntegrationError,
    LLMResponseError,
    LLMTimeoutError,
    LLMUnavailableError,
    OllamaCaseAnalysisClient,
)
from ai.llm.schemas import CaseAnalysisResult
from ai.priority.priority_engine import PriorityCalculationError, PriorityResult, calculate_priority
from backend.core.config import settings
from backend.models.ai_analysis import AIAnalysis
from backend.models.case import Case
from backend.models.user import User
from backend.services.case_service import _assert_can_modify, get_case_or_404


def _llm_error_detail(exc: LLMIntegrationError) -> str:
    """Return a stable, non-sensitive component status for hybrid responses."""

    if isinstance(exc, LLMTimeoutError):
        return "LLM analysis timed out"
    if isinstance(exc, LLMUnavailableError):
        return "LLM analysis is temporarily unavailable"
    return "LLM analysis returned an invalid response"


def _case_data(case: Case) -> dict[str, Any]:
    return {
        field: getattr(case, field)
        for field in (
            "description", "assistance_category", "people_affected", "country", "governorate",
            "city", "severity", "urgency", "required_resources", "estimated_funding", "current_funding",
        )
    }


def _authorized_case(db: Session, case_id: str, current_user: User) -> Case:
    case = get_case_or_404(db, case_id)
    _assert_can_modify(case, current_user)
    return case


def _save_analysis(db: Session, analysis: AIAnalysis) -> AIAnalysis:
    try:
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to save AI analysis") from exc
    return analysis


def analyze_case(
    db: Session, case_id: str, current_user: User, client: OllamaCaseAnalysisClient | None = None
) -> tuple[AIAnalysis, CaseAnalysisResult]:
    case = _authorized_case(db, case_id, current_user)
    try:
        result = (client or OllamaCaseAnalysisClient()).analyze(_case_data(case))
    except LLMTimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Case analysis timed out") from exc
    except LLMUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Case analysis is temporarily unavailable") from exc
    except LLMResponseError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Case analysis returned an invalid response") from exc
    analysis = AIAnalysis(
        case_id=case.case_id,
        analysis_type="llm_case_analysis",
        model_name=settings.OLLAMA_MODEL,
        result=result.model_dump_json(),
        analysis_metadata={"fields": list(result.model_dump().keys())},
    )
    return _save_analysis(db, analysis), result


def calculate_case_priority(db: Session, case_id: str, current_user: User) -> tuple[AIAnalysis, PriorityResult]:
    case = _authorized_case(db, case_id, current_user)
    try:
        result = calculate_priority(
            severity=case.severity,
            urgency=case.urgency,
            people_affected=case.people_affected,
            estimated_funding=case.estimated_funding,
            current_funding=case.current_funding,
            assistance_category=case.assistance_category,
        )
    except PriorityCalculationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Case cannot be priority scored") from exc
    case.priority = result.priority_level
    analysis = AIAnalysis(
        case_id=case.case_id,
        analysis_type="priority_calculation",
        result=json.dumps({"score": result.score, "priority_level": result.priority_level, "reasons": result.reasons}),
        analysis_metadata={"priority_score": result.score, "reasons": result.reasons},
    )
    return _save_analysis(db, analysis), result


def run_hybrid_analysis(
    db: Session,
    case_id: str,
    current_user: User,
    client: OllamaCaseAnalysisClient | None = None,
) -> tuple[AIAnalysis, CaseAnalysisResult | None, PriorityResult | None, list[str]]:
    """Orchestrate the available case AI components without coupling to absent modules.

    LLM and priority results are independent. A failure in either component is
    represented in the persisted hybrid result while a database write failure
    remains transactional and is surfaced to the API caller.
    """

    case = _authorized_case(db, case_id, current_user)
    llm_result: CaseAnalysisResult | None = None
    priority_result: PriorityResult | None = None
    unavailable_components: list[str] = []

    try:
        candidate = (client or OllamaCaseAnalysisClient()).analyze(_case_data(case))
        llm_result = CaseAnalysisResult.model_validate(candidate)
    except (LLMIntegrationError, ValueError) as exc:
        unavailable_components.append(_llm_error_detail(exc) if isinstance(exc, LLMIntegrationError) else "LLM analysis returned an invalid response")

    try:
        priority_result = calculate_priority(
            severity=case.severity,
            urgency=case.urgency,
            people_affected=case.people_affected,
            estimated_funding=case.estimated_funding,
            current_funding=case.current_funding,
            assistance_category=case.assistance_category,
        )
        case.priority = priority_result.priority_level
    except PriorityCalculationError:
        unavailable_components.append("Priority calculation could not be completed")

    result = {
        "llm_analysis": llm_result.model_dump() if llm_result else None,
        "priority": (
            {
                "score": priority_result.score,
                "priority_level": priority_result.priority_level,
                "reasons": priority_result.reasons,
            }
            if priority_result
            else None
        ),
        "unavailable_components": unavailable_components,
    }
    analysis = AIAnalysis(
        case_id=case.case_id,
        analysis_type="hybrid_case_analysis",
        model_name=settings.OLLAMA_MODEL if llm_result else None,
        result=json.dumps(result),
        analysis_metadata={"available_components": [name for name, value in (("llm", llm_result), ("priority", priority_result)) if value]},
    )
    return _save_analysis(db, analysis), llm_result, priority_result, unavailable_components
