from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.user import User
from backend.schemas.ai import AIAnalysisResponse, HybridAnalysisResponse, HybridPriorityResult, PriorityResponse
from backend.services.ai_service import analyze_case, calculate_case_priority, run_hybrid_analysis


router = APIRouter(prefix="/ai/cases", tags=["AI"])


@router.post("/{case_id}/analyze", response_model=AIAnalysisResponse)
def analyze(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis, result = analyze_case(db, case_id, current_user)
    return AIAnalysisResponse(
        analysis_id=analysis.id, case_id=case_id, analysis=result,
        model_name=analysis.model_name, created_at=analysis.created_at,
    )


@router.post("/{case_id}/calculate-priority", response_model=PriorityResponse)
def calculate_priority(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis, result = calculate_case_priority(db, case_id, current_user)
    return PriorityResponse(
        analysis_id=analysis.id, case_id=case_id, score=result.score,
        priority_level=result.priority_level, reasons=result.reasons, created_at=analysis.created_at,
    )


@router.post("/{case_id}/hybrid-analysis", response_model=HybridAnalysisResponse)
def hybrid_analysis(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis, llm_result, priority_result, unavailable_components = run_hybrid_analysis(
        db, case_id, current_user
    )
    return HybridAnalysisResponse(
        analysis_id=analysis.id,
        case_id=case_id,
        llm_analysis=llm_result,
        priority=(
            HybridPriorityResult(
                score=priority_result.score,
                priority_level=priority_result.priority_level,
                reasons=priority_result.reasons,
            )
            if priority_result
            else None
        ),
        unavailable_components=unavailable_components,
        created_at=analysis.created_at,
    )
