from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import InterviewCreate, InterviewRead, InterviewUpdate
from app.services import interviews as interview_service

router = APIRouter(prefix="/interviews", tags=["interviews"])

@router.post("", response_model=InterviewRead, status_code=status.HTTP_201_CREATED)
def create_interview(payload: InterviewCreate, db: Session = Depends(get_db)):
    # TODO: get user_id from auth token
    # for now, user_id will be passed in the payload
    return interview_service.create_interview(db, payload)

@router.get("/{interview_id}", response_model=InterviewRead)
def get_interview(interview_id: int, db: Session = Depends(get_db)):
    return interview_service.get_interview(db, interview_id)

@router.get("", response_model=List[InterviewRead])
def list_interviews(
    user_id: int = Query(..., description="Interviews for this user ID"), # TODO: get user_id from auth token
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return interview_service.list_interviews(db, user_id, limit, offset)

@router.patch("/{interview_id}", response_model=InterviewRead)
def update_interview(interview_id: int, payload: InterviewUpdate, db: Session = Depends(get_db)):
    return interview_service.update_interview(db, interview_id, payload)

@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview(interview_id: int, db: Session = Depends(get_db)):
    interview_service.delete_interview(db, interview_id)
    return None