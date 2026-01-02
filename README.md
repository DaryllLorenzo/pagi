# pagi

A minimal, ORM-agnostic pagination toolkit for Python.  
Define your pagination logic once, and paginate **efficiently** with SQLAlchemy, Django, raw SQL, or any data source — all wrapped in typed Pydantic models.

✨ **Features**
- ✅ Pydantic v2 models for `OffsetLimit` requests and `PaginatedResponse`

📦 **Install**
```bash
pip install pagi
# or with uv
uv pip install pagi
```

## Roadmap

Here’s what’s planned — contributions are welcome!

- [x] **Create repository and basic models**  

- [ ] **SQLAlchemy integration**  
  Implement strategy pattern to support both **async and sync sessions** 

- [ ] **Django ORM support**  
  Evaluate feasibility and provide `DataSource` examples for Django QuerySets.

- [ ] **Tortoise ORM support**  
  Assess API compatibility and document usage patterns.

- [ ] **Cursor-based pagination**  
  Add `CursorPaginator` and `CursorPaginatedResponse` as an alternative to offset/limit (for better performance on large datasets).

