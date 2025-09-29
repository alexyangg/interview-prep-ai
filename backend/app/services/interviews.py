from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db import models
from app.schemas import InterviewCreate, InterviewUpdate

def create_interview(db: Session, data: InterviewCreate) -> models.Interview:
    interview = models.Interview(**data.model_dump()) # .model_dump: Pydantic model to dict. **: construct new ORM object from dict
    db.add(interview)
    db.commit() # write to DB
    db.refresh(interview)
    return interview

def get_interview(db: Session, interview_id: int) -> models.Interview:
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")
    return interview

def list_interviews(
        db: Session, user_id: int, limit: int, offset: int
) -> list[models.Interview]:
    return (db.query(models.Interview)
            .filter(models.Interview.user_id == user_id)
            .order_by(models.Interview.id.desc()) # newest first
            .limit(limit)
            .offset(offset) # skip some rows for pagination
            .all() # return as a list of ORM objects
        )

# def list_interviews(
#     db: Session,
#     user_id: Optional[int],
#     pagination: PaginationParams
# ):
#     # base query
#     q = db.query(Interview)

#     # ✅ apply filter when user_id is provided
#     if user_id is not None:
#         q = q.filter(Interview.user_id == user_id)

#     total = q.count()
#     rows = (
#         q.order_by(Interview.created_at.desc())
#          .offset(pagination.offset)
#          .limit(pagination.limit)
#          .all()
#     )

#     # keep the same response shape you already return
#     return {
#         "items": rows,
#         "total": total,
#         "limit": pagination.limit,
#         "offset": pagination.offset,
#     }

def update_interview(db: Session, interview_id: int, data: InterviewUpdate) -> models.Interview:
    interview = get_interview(db, interview_id)
    for field, value in data.model_dump(exclude_unset=True).items(): # only update fields that are set
        setattr(interview, field, value) # setattr: update attribute of an object
    db.commit()
    db.refresh(interview)
    return interview

def delete_interview(db: Session, interview_id: int) -> None:
    interview = get_interview(db, interview_id)
    db.delete(interview)
    db.commit()
