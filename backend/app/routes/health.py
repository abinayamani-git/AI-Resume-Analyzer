"""Health check endpoint."""

from fastapi import APIRouter

from app.config import settings
from app.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/api/health", response_model=HealthResponse)
def health_check():
    """Simple liveness endpoint for frontend connectivity checks."""
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        ai_provider=settings.ai_provider if settings.openai_api_key else "fallback",
    )
