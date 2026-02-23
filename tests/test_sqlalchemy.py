from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from pydantic import ValidationError
import pytest

from paginator.paginator import paginate_sync


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


def test_sqlalchemy_pagination():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        session.add_all([User(name=f"user{i}") for i in range(30)])
        session.commit()

        result = paginate_sync(
            session,
            lambda: select(User),
            offset=10,
            limit=5,
            backend="sqlalchemy",
        )

    assert result.total == 30
    assert result.offset == 10
    assert result.limit == 5
    assert len(result.items) == 5
    assert result.items[0].name == "user10"


class TestSQLAlchemyEdgeCases:
    """Edge case tests for SQLAlchemy backend."""

    @pytest.fixture
    def session(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        with Session() as session:
            yield session

    def test_empty_result_set(self, session):
        """Query returns 0 records."""
        result = paginate_sync(
            session,
            lambda: select(User),
            offset=0,
            limit=10,
            backend="sqlalchemy",
        )
        assert result.total == 0
        assert result.offset == 0
        assert result.limit == 10
        assert len(result.items) == 0

    def test_first_page(self, session):
        """First page with offset=0, limit=N."""
        session.add_all([User(name=f"user{i}") for i in range(30)])
        session.commit()

        result = paginate_sync(
            session,
            lambda: select(User),
            offset=0,
            limit=10,
            backend="sqlalchemy",
        )
        assert result.total == 30
        assert result.offset == 0
        assert result.limit == 10
        assert len(result.items) == 10
        assert result.items[0].name == "user0"

    def test_last_page_partial(self, session):
        """Last page where limit exceeds remaining records."""
        session.add_all([User(name=f"user{i}") for i in range(25)])
        session.commit()

        result = paginate_sync(
            session,
            lambda: select(User),
            offset=20,
            limit=10,
            backend="sqlalchemy",
        )
        assert result.total == 25
        assert result.offset == 20
        assert result.limit == 10
        assert len(result.items) == 5
        assert result.items[0].name == "user20"
        assert result.items[-1].name == "user24"

    def test_exact_page_boundary(self, session):
        """Exact page boundary where offset + limit == total."""
        session.add_all([User(name=f"user{i}") for i in range(30)])
        session.commit()

        result = paginate_sync(
            session,
            lambda: select(User),
            offset=20,
            limit=10,
            backend="sqlalchemy",
        )
        assert result.total == 30
        assert result.offset == 20
        assert result.limit == 10
        assert len(result.items) == 10
        assert result.items[0].name == "user20"
        assert result.items[-1].name == "user29"

    def test_offset_beyond_total(self, session):
        """Offset > total should return empty items."""
        session.add_all([User(name=f"user{i}") for i in range(30)])
        session.commit()

        result = paginate_sync(
            session,
            lambda: select(User),
            offset=50,
            limit=10,
            backend="sqlalchemy",
        )
        assert result.total == 30
        assert result.offset == 50
        assert result.limit == 10
        assert len(result.items) == 0

    def test_maximum_limit(self, session):
        """Test with limit=100 (the configured maximum)."""
        session.add_all([User(name=f"user{i}") for i in range(150)])
        session.commit()

        result = paginate_sync(
            session,
            lambda: select(User),
            offset=0,
            limit=100,
            backend="sqlalchemy",
        )
        assert result.total == 150
        assert result.offset == 0
        assert result.limit == 100
        assert len(result.items) == 100

    def test_limit_zero_validation_error(self):
        """limit=0 should raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            paginate_sync(
                None,
                lambda: select(User),
                offset=0,
                limit=0,
                backend="sqlalchemy",
            )
        assert "limit" in str(exc_info.value)
        assert "gt=0" in str(exc_info.value).lower() or "greater than 0" in str(exc_info.value).lower()

    def test_limit_exceeds_maximum(self):
        """limit > 100 should raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            paginate_sync(
                None,
                lambda: select(User),
                offset=0,
                limit=101,
                backend="sqlalchemy",
            )
        assert "limit" in str(exc_info.value)
        assert "le=100" in str(exc_info.value).lower() or "less than or equal to 100" in str(exc_info.value).lower()

    def test_negative_offset_validation_error(self):
        """Negative offset should raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            paginate_sync(
                None,
                lambda: select(User),
                offset=-5,
                limit=10,
                backend="sqlalchemy",
            )
        assert "offset" in str(exc_info.value)
        assert "ge=0" in str(exc_info.value).lower() or "greater than or equal to 0" in str(exc_info.value).lower()
