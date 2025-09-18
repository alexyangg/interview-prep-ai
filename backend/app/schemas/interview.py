from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

# reuse across create/update/read
class InterviewBase(BaseModel):
    company: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, max_length=100)
    # can add more types later
    type: Optional[Literal["phone", "behavioural", "coding", "design"]] = None
    source: Optional[Literal["gmail", "gcal"]] = None
    starts_at: Optional[datetime] = None
    details: Optional[dict[str, Any]] = None

    # from_attributes=True for reading from ORM objects
    model_config = ConfigDict(from_attributes=True) 

    # ensure datetime has timezone info
    @field_validator("starts_at")
    @classmethod
    def ensure_timezone(cls, dt: Optional[datetime]) -> Optional[datetime]:
        if dt is None:
            return dt
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    
# POST /interviews
class InterviewCreate(InterviewBase):
    user_id: int

# PATCH /interviews/{id}
class InterviewUpdate(InterviewBase):
    pass

# GET /interviews/{id}
class InterviewRead(InterviewBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None