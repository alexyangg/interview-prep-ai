from fastapi import APIRouter
from app.api.interviews import router as interviews_router
from app.api.users import router as users_router

router = APIRouter()

# check if API is running
@router.get("/health")
def v1_health():
    return {"status": "ok", "scope": "v1"}

router.include_router(interviews_router)
router.include_router(users_router)