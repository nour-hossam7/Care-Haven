from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.security import get_current_user
from backend.core.database import get_db
from backend.models.user import User
from backend.services.assistant_service import answer_live_question, is_live_question, is_mixed_question
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.rag_service import ask_question


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if is_live_question(payload.question):
        live_answer = answer_live_question(db, payload.question)
        if is_mixed_question(payload.question):
            knowledge = ask_question(payload.question)
            return {
                "answer": f"{live_answer}\n\nContext from the humanitarian knowledge base:\n{knowledge['answer']}",
                "sources": knowledge["sources"],
            }
        return {"answer": live_answer, "sources": []}
    return ask_question(payload.question)