from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas import UserCreate, UserUpdate, UserRead, ErrorResponse
from app.services import users as svc

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED,
             responses={409: {"model": ErrorResponse}})
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    return svc.create_user(db, payload)

@router.get("/{user_id}", response_model=UserRead,
            responses={404: {"model": ErrorResponse}})
def get_user(user_id: int, db: Session = Depends(get_db)):
    return svc.get_user(db, user_id)

@router.get("", response_model=List[UserRead])
def list_users(
    email: Optional[str] = Query(None, description="Filter by exact email"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(svc.models.User)  # reuse model via service module
    if email:
        q = q.filter(svc.models.User.email == email)
    return q.order_by(svc.models.User.id.desc()).offset(offset).limit(limit).all()

@router.patch("/{user_id}", response_model=UserRead,
              responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}})
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    return svc.update_user(db, user_id, payload)
    
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT,
               responses={404: {"model": ErrorResponse}})
def delete_user(user_id: int, db: Session = Depends(get_db)):
    svc.delete_user(db, user_id)
    return None