from typing import Any, Callable
from .models import PaginatedResponse, OffsetLimitPaginator
from .strategies.base import PaginationStrategy
from .strategies.sqlalchemy import create_sqlalchemy_strategy

async def paginate(
    connection: Any,
    query_func: Callable[[], Any],
    *,
    offset: int = 0,
    limit: int = 10,
    backend: str = "sqlalchemy"
) -> PaginatedResponse:
    """
    Perform asynchronous pagination using the specified ORM backend.

    Args:
        connection (Any): ORM context (e.g., SQLAlchemy AsyncSession).
        query_func (Callable[[], Any]): Callable returning a non-executed query.
        offset (int): Number of records to skip. Must be >= 0. Default: 0.
        limit (int): Number of records to return. Must be 1–100. Default: 10.
        backend (str): ORM backend. Default: "sqlalchemy".

    Returns:
        PaginatedResponse

    Raises:
        ValidationError: If offset/limit violate Pydantic constraints.
        ValueError / NotImplementedError: See `_get_strategy`.

    Example:
        result = await paginate(session, lambda: select(User), offset=20, limit=10)
    """
    # Validate using Pydantic model (reuses your validation logic!)
    paginator = OffsetLimitPaginator(offset=offset, limit=limit)
    strategy = _get_strategy(connection, backend)
    return await strategy.paginate_async(query_func, paginator.offset, paginator.limit)


def paginate_sync(
    connection: Any,
    query_func: Callable[[], Any],
    *,
    offset: int = 0,
    limit: int = 10,
    backend: str = "sqlalchemy"
) -> PaginatedResponse:
    """
    Perform synchronous pagination.

    Same as `paginate`, but for sync contexts.

    Example:
        result = paginate_sync(session, lambda: select(User), offset=20, limit=10)
    """
    paginator = OffsetLimitPaginator(offset=offset, limit=limit)
    strategy = _get_strategy(connection, backend)
    return strategy.paginate_sync(query_func, paginator.offset, paginator.limit)


def _get_strategy(connection: Any, backend: str) -> PaginationStrategy:
    """
    Internal factory function that returns the appropriate pagination strategy.

    Args:
        connection: The ORM connection/context (usage depends on backend, sqlalchemy -> session for example.).
        backend: Name of the backend (e.g., "sqlalchemy").

    Returns:
        An instance of a PaginationStrategy subclass.

    Raises:
        ValueError: If backend is unknown.
        NotImplementedError: If backend is known but not implemented yet.
    """
    if backend == "sqlalchemy":
        return create_sqlalchemy_strategy(connection)
    elif backend == "django":
        # Will be implemented later
        raise NotImplementedError("Django backend support is not yet implemented.")
    elif backend == "tortoise":
        # Will be implemented later
        raise NotImplementedError("Tortoise-ORM backend support is not yet implemented.")
    else:
        supported = ["sqlalchemy", "django", "tortoise"]
        raise ValueError(
            f"Unsupported backend: '{backend}'. Supported backends: {supported}."
        )