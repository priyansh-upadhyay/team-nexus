from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/check", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", detail="Service is available")
