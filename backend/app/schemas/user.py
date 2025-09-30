from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    google_sub: Optional[str] = Field(None, max_length=128) # globally unique identifier for user in Google's system

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    pass # google_sub optional for now

class UserRead(UserBase):
    id: int

class UserUpdate(UserBase):
    email: Optional[EmailStr] = Field(None, max_length=255)
    google_sub: Optional[str] = Field(None, max_length=128)

    model_config = ConfigDict(from_attributes=True)
