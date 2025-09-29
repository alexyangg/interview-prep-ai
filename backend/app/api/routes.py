from fastapi import APIRouter
from app.api.interviews import router as interviews_router

router = APIRouter()

# check if API is running
@router.get("/health")
def v1_health():
    return {"status": "ok", "scope": "v1"}

# Legacy endpoint moved to interviews.py router
# Keeping DEFAULT_INTERVIEW_LIMIT for reference but not used anymore

router.include_router(interviews_router)