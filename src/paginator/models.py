from pydantic import BaseModel, Field
from typing import Generic, TypeVar

T = TypeVar("T")

class OffsetLimitPaginator(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(10, gt=0, le=100)

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    offset: int
    limit: int