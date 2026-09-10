from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.user import User
from backend.schemas.recommendation import RecommendationCase
from backend.services.recommendation_service import get_donor_recommendations


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/{donor_id}", response_model=list[RecommendationCase])
def get_recommendations(
    donor_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_donor_recommendations(db, donor_id)