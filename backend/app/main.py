from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.users.router import router as users_router
from app.api.routes.health import router as health_router

from app.db import Base, engine
from app.users import models as users_models  # noqa: F401

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await engine.dispoze()

app = FastAPI(
    title="Rachunko API",
    description="API do wspólnego ewidencjonowania i rozliczania wydatków.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(users_router)

@app.get("/", tags=["Informacje"])
def root() -> dict[str, str]:
    return {"name": "Rachunko API", "docs": "/docs", "health": "/api/health"}
