from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import (
    InterviewCreate, 
    InterviewRead, 
    InterviewUpdate,
    ErrorResponse
)
from app.services import interviews as interview_service
from app.schemas.common import PaginationParams
from app.api.deps import pagination_params

router = APIRouter(prefix="/interviews", tags=["interviews"])

@router.post(
    "", 
    response_model=InterviewRead, 
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": ErrorResponse}}
)
def create_interview(payload: InterviewCreate, db: Session = Depends(get_db)):
    # TODO: get user_id from auth token
    # for now, user_id will be passed in the payload
    return interview_service.create_interview(db, payload)

@router.get(
    "/{interview_id}", 
    response_model=InterviewRead,
    responses={404: {"model": ErrorResponse}}
)
def get_interview(interview_id: int, db: Session = Depends(get_db)):
    return interview_service.get_interview(db, interview_id)

@router.get(
    "", 
    response_model=List[InterviewRead],
    responses={404: {"model": ErrorResponse}}
)
def list_interviews(
    user_id: int = Query(..., description="Interviews for this user ID"), # TODO: get user_id from auth token
    pagination: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db)
):
    return interview_service.list_interviews(db, user_id, pagination.limit, pagination.offset)

@router.patch(
    "/{interview_id}", 
    response_model=InterviewRead,
    responses={404: {"model": ErrorResponse}}
)
def update_interview(interview_id: int, payload: InterviewUpdate, db: Session = Depends(get_db)):
    return interview_service.update_interview(db, interview_id, payload)

@router.delete(
    "/{interview_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}}
)
def delete_interview(interview_id: int, db: Session = Depends(get_db)):
    interview_service.delete_interview(db, interview_id)
    return None