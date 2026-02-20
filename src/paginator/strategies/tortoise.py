# pagi/strategies/tortoise.py
from typing import Any, Callable, Generic, TypeVar
from tortoise.queryset import QuerySet
from ..models import PaginatedResponse
from .base import PaginationStrategy

T = TypeVar("T")


class TortoisePaginationStrategy(PaginationStrategy[T], Generic[T]):
    """
    Pagination strategy for Tortoise ORM.
    
    Tortoise ORM is async-first, so paginate_async is the primary method.
    paginate_sync raises RuntimeError (similar to Django backend).
    """

    def __init__(self, connection: Any = None):
        # connection is unused, but kept for API consistency
        self.connection = connection

    async def paginate_async(
        self,
        query_func: Callable[[], QuerySet],
        offset: int,
        limit: int,
    ) -> PaginatedResponse[T]:

        queryset = query_func()

        if not isinstance(queryset, QuerySet):
            raise TypeError(
                "Tortoise backend requires query_func to return a Tortoise QuerySet."
            )

        total = await queryset.count()
        items = await queryset.offset(offset).limit(limit)

        return PaginatedResponse(
            items=items,
            total=total,
            offset=offset,
            limit=limit,
        )

    def paginate_sync(
        self,
        query_func: Callable[[], Any],
        offset: int,
        limit: int,
    ) -> PaginatedResponse[T]:
        raise RuntimeError(
            "Sync pagination is not supported by Tortoise ORM. "
            "Use paginate_async or wrap it with asyncio.run()."
        )


def create_tortoise_strategy(connection: Any = None) -> PaginationStrategy:
    """
    Factory function for Tortoise ORM backend.
    
    Tortoise doesn't use sessions like SQLAlchemy; models are global.
    The connection parameter is kept for API consistency but unused.
    """
    return TortoisePaginationStrategy(connection)
