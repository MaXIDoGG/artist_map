from fastapi import APIRouter

from backend.core.config import get_settings
from backend.schemas import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", app=get_settings().app_name)
