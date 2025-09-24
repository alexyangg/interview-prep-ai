from fastapi import Query
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str

class PaginationParams(BaseModel):
    limit: int = Query(50, ge=1, le=100)
    offset: int = Query(0, ge=0)