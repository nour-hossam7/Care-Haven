from fastapi import FastAPI

from backend.routers.auth import router as auth_router
from backend.routers.cases import router as cases_router


app = FastAPI(
    title="Care-Haven API",
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(cases_router)
