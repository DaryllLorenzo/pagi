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

- [x] **SQLAlchemy integration**  
  Implement strategy pattern to support both **async and sync sessions** 

- [ ] **Django ORM support**  
  Evaluate feasibility and provide `DataSource` examples for Django QuerySets.

- [ ] **Tortoise ORM support**  
  Assess API compatibility and document usage patterns.

- [ ] **Cursor-based pagination**  
  Add `CursorPaginator` and `CursorPaginatedResponse` as an alternative to offset/limit (for better performance on large datasets).

¡Claro! Aquí tienes una actualización **breve, clara y profesional** del README que menciona el diseño basado en patrones y la estructura interna, sin alargarse:


## 🧠 Design & Architecture

`pagi` is built around the **Strategy pattern**, allowing it to support multiple ORMs while keeping the core API simple and unified.  

- **`paginator.py`** provides the public API (`paginate`, `paginate_sync`) and delegates to backend-specific strategies.
- Each ORM (e.g., SQLAlchemy) implements a **concrete strategy** that handles its own session/query mechanics.
- Pagination logic is **decoupled from data sources**, making it easy to extend to Django, Tortoise, or custom backends.


### SQLAlchemy

The SQLAlchemy integration uses a **factory-based strategy** to automatically select the right execution mode:

- When you pass a `Session`, `pagi` uses a **synchronous strategy**.
- When you pass an `AsyncSession`, it switches to an **asynchronous strategy**.
- The factory (`create_sqlalchemy_strategy`) inspects the session type and instantiates the appropriate paginator internally — **no configuration needed**.

This ensures you always use the correct execution model (`paginate_sync` ↔ sync session, `paginate` ↔ async session).