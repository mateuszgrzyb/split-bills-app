from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router

app = FastAPI(
    title="Rachunko API",
    description="API do wspólnego ewidencjonowania i rozliczania wydatków.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")


@app.get("/", tags=["Informacje"])
def root() -> dict[str, str]:
    return {"name": "Rachunko API", "docs": "/docs", "health": "/api/health"}
