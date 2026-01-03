# pagi/strategies/base.py
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar
from ..models import PaginatedResponse

T = TypeVar("T")

class PaginationStrategy(ABC, Generic[T]):
    """
    Abstract base class for pagination strategies across different ORMs.
    
    Each ORM (SQLAlchemy, Django, etc.) must implement this interface.
    """

    @abstractmethod
    async def paginate_async(
        self,
        query_func: Callable[[], Any],
        offset: int,
        limit: int,
    ) -> PaginatedResponse[T]:
        """Perform async pagination."""
        raise NotImplementedError

    @abstractmethod
    def paginate_sync(
        self,
        query_func: Callable[[], Any],
        offset: int,
        limit: int,
    ) -> PaginatedResponse[T]:
        """Perform sync pagination."""
        raise NotImplementedError