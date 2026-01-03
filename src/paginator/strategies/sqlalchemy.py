# pagi/strategies/sqlalchemy.py
from typing import Any, Callable, Generic, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, func, select
from ..models import PaginatedResponse
from .base import PaginationStrategy

T = TypeVar("T")

class SQLAlchemySyncPaginationStrategy(PaginationStrategy[T], Generic[T]):
    def __init__(self, session: Session):
        self.session = session

    def paginate_sync(
        self,
        query_func: Callable[[], Select],
        offset: int,
        limit: int,
    ) -> PaginatedResponse[T]:
        
        stmt = query_func().offset(offset).limit(limit)
        original = query_func()
        count_stmt = select(func.count()).select_from(original.subquery())
        items = self.session.execute(stmt).scalars().all()
        total = self.session.execute(count_stmt).scalar_one()
        return PaginatedResponse(items=items, total=total, offset=offset, limit=limit)

    def paginate_async(
        self,
        query_func: Callable[[], Any],
        offset: int,
        limit: int,
    )-> PaginatedResponse[T]:
        raise RuntimeError(
            "Async pagination is not supported with a synchronous SQLAlchemy Session. "
            "Use `paginate_sync` or an `AsyncSession`."
        )


class SQLAlchemyAsyncPaginationStrategy(PaginationStrategy[T], Generic[T]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def paginate_async(
        self,
        query_func: Callable[[], Select],
        offset: int,
        limit: int,
    ) -> PaginatedResponse[T]:
        
        stmt = query_func().offset(offset).limit(limit)
        original = query_func()
        count_stmt = select(func.count()).select_from(original.subquery())
        items_result = await self.session.execute(stmt)
        total_result = await self.session.execute(count_stmt)
        items = items_result.scalars().all()
        total = total_result.scalar_one()
        return PaginatedResponse(items=items, total=total, offset=offset, limit=limit)

    def paginate_sync(
        self,
        query_func: Callable[[], Any],
        offset: int,
        limit: int,
    )-> PaginatedResponse[T]:
        raise RuntimeError(
            "Sync pagination is not supported with an asynchronous SQLAlchemy Session. "
            "Use `paginate` (async) or a synchronous `Session`."
        )


def create_sqlalchemy_strategy(connection: Any) -> PaginationStrategy:
    """
    Factory function for SQLAlchemy backend.
    Inspects the connection type and returns the appropriate strategy.
    """
    if isinstance(connection, AsyncSession):
        return SQLAlchemyAsyncPaginationStrategy(connection)
    elif isinstance(connection, Session):
        return SQLAlchemySyncPaginationStrategy(connection)
    else:
        raise TypeError(
            "SQLAlchemy backend requires a sqlalchemy.orm.Session or "
            "sqlalchemy.ext.asyncio.AsyncSession instance."
        )