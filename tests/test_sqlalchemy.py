from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column

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
