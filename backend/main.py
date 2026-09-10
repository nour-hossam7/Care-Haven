from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.routers.auth import router as auth_router
from backend.routers.ai import router as ai_router
from backend.routers.cases import router as cases_router
from backend.routers.chat import router as chat_router
from backend.routers.donations import case_donations_router, router as donations_router
from backend.routers.evidence import router as evidence_router
from backend.routers.recommendations import router as recommendations_router


app = FastAPI(
    title="Care-Haven API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(ai_router)
app.include_router(cases_router)
app.include_router(chat_router)
app.include_router(donations_router)
app.include_router(case_donations_router)
app.include_router(evidence_router)
app.include_router(recommendations_router)