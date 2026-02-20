# pagi

A minimal, ORM-agnostic pagination toolkit for Python.

`pagi` lets you define pagination logic once and reuse it across different ORMs (SQLAlchemy, Django, etc.), returning consistent, typed responses powered by Pydantic.

---

## Features

* Offset/limit pagination with validation via Pydantic
* Unified response model (`PaginatedResponse`)
* SQLAlchemy support (sync and async)
* Django ORM support
* Tortoise ORM support
* Strategy-based internal design for easy extensibility
* ORM-agnostic public API

---

## Installation

```bash
pip install pagi
```

Or with development dependencies:

```bash
pip install -e .[dev]
```

or if you are using uv

```bash
uv pip install -e .[dev]
```


## Basic Usage

### Importing

The installable package name is `pagi`, but the Python module is `paginator`.

Recommended import:

```python
from paginator.paginator import paginate, paginate_sync
```

---

## SQLAlchemy (Synchronous)

```python
from sqlalchemy import select
from sqlalchemy.orm import Session
from paginator import paginate_sync

def get_users(session: Session):
    return paginate_sync(
        session,
        lambda: select(User),
        offset=10,
        limit=5,
        backend="sqlalchemy",
    )
```


## SQLAlchemy (Asynchronous)

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from paginator import paginate

async def get_users(session: AsyncSession):
    return await paginate(
        session,
        lambda: select(User),
        offset=10,
        limit=5,
        backend="sqlalchemy",
    )
```

The correct strategy (sync vs async) is selected automatically based on the session type.

---

## Django ORM

```python
from paginator import paginate_sync
from myapp.models import User

result = paginate_sync(
    connection=None,
    query_func=lambda: User.objects.all(),
    offset=20,
    limit=10,
    backend="django",
)
```

Notes:

* `query_func` must return an unevaluated Django `QuerySet`
* Django pagination is synchronous (async execution is not supported)


## Tortoise ORM

```python
from paginator import paginate
from myapp.models import User

result = await paginate(
    connection=None,
    query_func=lambda: User.all().order_by("id"),
    offset=20,
    limit=10,
    backend="tortoise",
)
```

Notes:

* Tortoise ORM is async-first, so only `paginate()` (async) is supported
* `paginate_sync()` will raise a `RuntimeError`
* Make sure Tortoise is initialized before calling pagination functions


## Design and Architecture

`pagi` is built around the **Strategy pattern**, allowing multiple ORMs to be supported while keeping a single, simple public API.

* `paginator.paginator` exposes the public functions (`paginate`, `paginate_sync`)
* Each ORM implements its own pagination strategy
* A small factory selects the appropriate strategy at runtime based on the backend and connection type
* Pagination logic is decoupled from data access, making new backends easy to add

### SQLAlchemy Strategy Selection

For SQLAlchemy, `pagi` uses a factory-based approach:

* Passing a `Session` enables synchronous pagination
* Passing an `AsyncSession` enables asynchronous pagination
* The correct strategy is chosen automatically without extra configuration

---

## Roadmap

* Cursor-based pagination (cursor tokens instead of offset/limit)
* Optional total count for performance-sensitive queries

---

## Testing and Edge Cases

The following edge cases should be considered when testing pagination across all backends:

### Common Edge Cases

* **Empty result set** - Query returns 0 records
* **First page** - `offset=0, limit=N`
* **Last page (partial)** - Requested limit exceeds remaining records
* **Exact page boundary** - `offset + limit == total`
* **Offset beyond total** - `offset > total` should return empty items
* **Maximum limit** - Test with `limit=100` (the configured maximum)
* **Limit validation** - `limit=0` or `limit > 100` should raise validation errors
* **Negative offset** - Should raise validation errors

### Backend-Specific Considerations

| Backend | Sync | Async | Notes |
|---------|------|-------|-------|
| SQLAlchemy | yes | yes | Strategy auto-selected by Session type |
| Django | yes | no | Wrap with `sync_to_async` if needed |
| Tortoise | no | yes | Async-first ORM |

---

## Development

Run tests with:

```bash
pytest
```

The test suite covers:

* SQLAlchemy (sync)
* Django ORM
* Tortoise ORM

---

## License

MIT

