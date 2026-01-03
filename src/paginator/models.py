from pydantic import BaseModel, Field
from typing import Generic, TypeVar

T = TypeVar("T")

class OffsetLimitPaginator(BaseModel):
    """
    Input model for offset-limit based pagination.

    Controls how many records to skip (`offset`) and how many to return (`limit`).
    Useful for clients to request specific pages of data.
    """
    offset: int = Field(0, ge=0, description="Number of records to skip. Must be >= 0")
    limit: int = Field(10, gt=0, le=100, description="Number of records to return. Must be between 1 and 100")

class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic container for paginated results.

    This model is meant to be returned by APIs that support pagination.
    It includes the actual items, total count, and pagination metadata.
    """
    items: list[T]
    total: int = Field(description="Total number of records matching the query (ignoring pagination).")
    offset: int = Field(description="Offset used in this response")
    limit: int = Field(description="Limit used in this response")