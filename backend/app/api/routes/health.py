from fastapi import APIRouter
from app.config import settings

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ai-suspicious-message-investigation-agent",
        "database_configured": bool(settings.supabase_url and settings.supabase_service_role_key),
        "llm_configured": bool(settings.gemini_api_key),
        "gemini_model": settings.gemini_model,
        "app_env": settings.app_env,
    }
