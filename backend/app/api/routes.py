from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db import models

DEFAULT_INTERVIEW_LIMIT = 50

router = APIRouter()

# check if API is running
@router.get("/health")
def v1_health():
    return {"status": "ok", "scope": "v1"}

# fetches up to DEFAULT_INTERVIEW_LIMIT interviews as JSON, sorted by most recent first
@router.get("/interviews")
def list_interviews(db: Session = Depends(get_db)):

    items = db.query(models.Interview)\
              .order_by(models.Interview.id.desc())\
              .limit(DEFAULT_INTERVIEW_LIMIT)\
              .all()
    
    # manual serialization - convert SQLAlchemy objects to JSON-compatible dicts
    return {
        "items": [
            {
                "id": item.id,
                "company": item.company,
                "role": item.role,
                "type": item.type,
                "starts_at": item.starts_at.isoformat() if item.starts_at else None,
            } 
            for item in items
        ]
    }

