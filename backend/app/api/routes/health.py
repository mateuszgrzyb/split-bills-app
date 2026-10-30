from fastapi import APIRouter

router = APIRouter(tags=["Status"])


@router.get("/health")
def health() -> dict[str, str]:
    """Prosty endpoint do sprawdzenia, czy API działa."""
    return {"status": "ok", "service": "rachunko-api"}
