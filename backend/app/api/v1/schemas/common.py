from pydantic import BaseModel
from typing import Optional, Generic, TypeVar, List
from datetime import datetime

T = TypeVar('T')

class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class ErrorResponse(BaseModel):
    error_type: str
    message: str
    timestamp: datetime
    details: Optional[dict] = None