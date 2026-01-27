# pagi/strategies/django.py
from typing import Any, Callable, Generic, TypeVar
from django.db.models import QuerySet
from ..models import PaginatedResponse
from .base import PaginationStrategy

T = TypeVar("T")


class DjangoPaginationStrategy(PaginationStrategy[T], Generic[T]):
    """
    Pagination strategy for Django ORM.
    """

    def __init__(self, connection: Any = None):
        # connection is unused, but kept for API consistency
        self.connection = connection

    def paginate_sync(
        self,
        query_func: Callable[[], QuerySet],
        offset: int,
        limit: int,
    ) -> PaginatedResponse[T]:

        queryset = query_func()

        if not isinstance(queryset, QuerySet):
            raise TypeError(
                "Django backend requires query_func to return a Django QuerySet."
            )

        total = queryset.count()
        items = list(queryset[offset : offset + limit])

        return PaginatedResponse(
            items=items,
            total=total,
            offset=offset,
            limit=limit,
        )

    def paginate_async(
        self,
        query_func: Callable[[], Any],
        offset: int,
        limit: int,
    ) -> PaginatedResponse[T]:
        raise RuntimeError(
            "Async pagination is not supported by Django ORM. "
            "Use paginate_sync or wrap it with sync_to_async."
        )


def create_django_strategy(connection: Any = None) -> PaginationStrategy:
    """
    Factory function for Django backend.
    """
    return DjangoPaginationStrategy(connection)
