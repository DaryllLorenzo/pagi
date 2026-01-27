# pagi

A minimal, ORM-agnostic pagination toolkit for Python.

`pagi` lets you define pagination logic once and reuse it across different ORMs (SQLAlchemy, Django, etc.), returning consistent, typed responses powered by Pydantic.

---

## Features

* Offset/limit pagination with validation via Pydantic
* Unified response model (`PaginatedResponse`)
* SQLAlchemy support (sync and async)
* Django ORM support
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

---

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

---

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

---

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
* Tortoise ORM support
* Optional total count for performance-sensitive queries

---

## Development

Run tests with:

```bash
pytest
```

The test suite covers:

* SQLAlchemy (sync)
* SQLAlchemy (async, optional)
* Django ORM

---

## License

MIT

