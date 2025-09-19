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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inteerview not found")
    return interview

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

def list_interviews(
        db: Session, user_id: int, limit: int = 50, offset: int = 0
) -> list[models.Interview]:
    return (db.query(models.Interview)
            .filter(models.Interview.user_id == user_id)
            .order_by(models.Interview.id.desc()) # newest first
            .limit(limit)
            .offset(offset) # skip some rows for pagination
            .all() # return as a list of ORM objects
)