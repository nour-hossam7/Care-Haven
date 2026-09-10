from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.core.security import get_current_user
from backend.models.user import User
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.rag_service import ask_question


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    return ask_question(payload.question)