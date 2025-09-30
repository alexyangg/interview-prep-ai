from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db import models
from app.schemas import UserCreate, UserUpdate

def create_user(db: Session, data: UserCreate) -> models.User:
    existing_user = db.query(models.User).filter(models.User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    user = models.User(**data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()

def update_user(db: Session, user_id: int, data: UserUpdate) -> models.User:
    user = get_user(db, user_id)
    patch = data.model_dump(exclude_unset=True)
    if "email" in patch:
        # enforce unique email
        q = db.query(models.User).filter(models.User.email == patch["email"], models.User.id != user_id)
        if db.query(q.exists()).scalar():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    for k, v in patch.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> None:
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()