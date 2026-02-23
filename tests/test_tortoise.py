import asyncio
from tortoise import Tortoise, fields, models
from pydantic import ValidationError
import pytest

from paginator.paginator import paginate


class User(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100)

    class Meta:
        table = "users"


def test_tortoise_pagination():
    """Test pagination with Tortoise ORM backend."""

    async def run_test():
        # Initialize Tortoise ORM
        await Tortoise.init(
            db_url="sqlite://:memory:",
            modules={"models": ["tests.test_tortoise"]},
        )
        await Tortoise.generate_schemas()

        try:
            # Create test data
            await User.bulk_create([User(name=f"user{i}") for i in range(50)])

            result = await paginate(
                connection=None,
                query_func=lambda: User.all().order_by("id"),
                offset=20,
                limit=10,
                backend="tortoise",
            )

            assert result.total == 50
            assert result.offset == 20
            assert result.limit == 10
            assert len(result.items) == 10
            assert result.items[0].name == "user20"
        finally:
            await Tortoise.close_connections()

    asyncio.run(run_test())


class TestTortoiseEdgeCases:
    """Edge case tests for Tortoise ORM backend."""

    def test_empty_result_set(self):
        """Query returns 0 records."""

        async def run_test():
            await Tortoise.init(
                db_url="sqlite://:memory:",
                modules={"models": ["tests.test_tortoise"]},
            )
            await Tortoise.generate_schemas()

            try:
                result = await paginate(
                    connection=None,
                    query_func=lambda: User.all().order_by("id"),
                    offset=0,
                    limit=10,
                    backend="tortoise",
                )
                assert result.total == 0
                assert result.offset == 0
                assert result.limit == 10
                assert len(result.items) == 0
            finally:
                await Tortoise.close_connections()

        asyncio.run(run_test())

    def test_first_page(self):
        """First page with offset=0, limit=N."""

        async def run_test():
            await Tortoise.init(
                db_url="sqlite://:memory:",
                modules={"models": ["tests.test_tortoise"]},
            )
            await Tortoise.generate_schemas()

            try:
                await User.bulk_create([User(name=f"user{i}") for i in range(30)])

                result = await paginate(
                    connection=None,
                    query_func=lambda: User.all().order_by("id"),
                    offset=0,
                    limit=10,
                    backend="tortoise",
                )
                assert result.total == 30
                assert result.offset == 0
                assert result.limit == 10
                assert len(result.items) == 10
                assert result.items[0].name == "user0"
            finally:
                await Tortoise.close_connections()

        asyncio.run(run_test())

    def test_last_page_partial(self):
        """Last page where limit exceeds remaining records."""

        async def run_test():
            await Tortoise.init(
                db_url="sqlite://:memory:",
                modules={"models": ["tests.test_tortoise"]},
            )
            await Tortoise.generate_schemas()

            try:
                await User.bulk_create([User(name=f"user{i}") for i in range(25)])

                result = await paginate(
                    connection=None,
                    query_func=lambda: User.all().order_by("id"),
                    offset=20,
                    limit=10,
                    backend="tortoise",
                )
                assert result.total == 25
                assert result.offset == 20
                assert result.limit == 10
                assert len(result.items) == 5
                assert result.items[0].name == "user20"
                assert result.items[-1].name == "user24"
            finally:
                await Tortoise.close_connections()

        asyncio.run(run_test())

    def test_exact_page_boundary(self):
        """Exact page boundary where offset + limit == total."""

        async def run_test():
            await Tortoise.init(
                db_url="sqlite://:memory:",
                modules={"models": ["tests.test_tortoise"]},
            )
            await Tortoise.generate_schemas()

            try:
                await User.bulk_create([User(name=f"user{i}") for i in range(30)])

                result = await paginate(
                    connection=None,
                    query_func=lambda: User.all().order_by("id"),
                    offset=20,
                    limit=10,
                    backend="tortoise",
                )
                assert result.total == 30
                assert result.offset == 20
                assert result.limit == 10
                assert len(result.items) == 10
                assert result.items[0].name == "user20"
                assert result.items[-1].name == "user29"
            finally:
                await Tortoise.close_connections()

        asyncio.run(run_test())

    def test_offset_beyond_total(self):
        """Offset > total should return empty items."""

        async def run_test():
            await Tortoise.init(
                db_url="sqlite://:memory:",
                modules={"models": ["tests.test_tortoise"]},
            )
            await Tortoise.generate_schemas()

            try:
                await User.bulk_create([User(name=f"user{i}") for i in range(30)])

                result = await paginate(
                    connection=None,
                    query_func=lambda: User.all().order_by("id"),
                    offset=50,
                    limit=10,
                    backend="tortoise",
                )
                assert result.total == 30
                assert result.offset == 50
                assert result.limit == 10
                assert len(result.items) == 0
            finally:
                await Tortoise.close_connections()

        asyncio.run(run_test())

    def test_maximum_limit(self):
        """Test with limit=100 (the configured maximum)."""

        async def run_test():
            await Tortoise.init(
                db_url="sqlite://:memory:",
                modules={"models": ["tests.test_tortoise"]},
            )
            await Tortoise.generate_schemas()

            try:
                await User.bulk_create([User(name=f"user{i}") for i in range(150)])

                result = await paginate(
                    connection=None,
                    query_func=lambda: User.all().order_by("id"),
                    offset=0,
                    limit=100,
                    backend="tortoise",
                )
                assert result.total == 150
                assert result.offset == 0
                assert result.limit == 100
                assert len(result.items) == 100
            finally:
                await Tortoise.close_connections()

        asyncio.run(run_test())

    def test_limit_zero_validation_error(self):
        """limit=0 should raise validation error."""

        async def run_test():
            await Tortoise.init(
                db_url="sqlite://:memory:",
                modules={"models": ["tests.test_tortoise"]},
            )
            await Tortoise.generate_schemas()

            try:
                with pytest.raises(ValidationError) as exc_info:
                    await paginate(
                        connection=None,
                        query_func=lambda: User.all().order_by("id"),
                        offset=0,
                        limit=0,
                        backend="tortoise",
                    )
                assert "limit" in str(exc_info.value)
                assert "gt=0" in str(exc_info.value).lower() or "greater than 0" in str(exc_info.value).lower()
            finally:
                await Tortoise.close_connections()

        asyncio.run(run_test())

    def test_limit_exceeds_maximum(self):
        """limit > 100 should raise validation error."""

        async def run_test():
            await Tortoise.init(
                db_url="sqlite://:memory:",
                modules={"models": ["tests.test_tortoise"]},
            )
            await Tortoise.generate_schemas()

            try:
                with pytest.raises(ValidationError) as exc_info:
                    await paginate(
                        connection=None,
                        query_func=lambda: User.all().order_by("id"),
                        offset=0,
                        limit=101,
                        backend="tortoise",
                    )
                assert "limit" in str(exc_info.value)
                assert "le=100" in str(exc_info.value).lower() or "less than or equal to 100" in str(exc_info.value).lower()
            finally:
                await Tortoise.close_connections()

        asyncio.run(run_test())

    def test_negative_offset_validation_error(self):
        """Negative offset should raise validation error."""

        async def run_test():
            await Tortoise.init(
                db_url="sqlite://:memory:",
                modules={"models": ["tests.test_tortoise"]},
            )
            await Tortoise.generate_schemas()

            try:
                with pytest.raises(ValidationError) as exc_info:
                    await paginate(
                        connection=None,
                        query_func=lambda: User.all().order_by("id"),
                        offset=-5,
                        limit=10,
                        backend="tortoise",
                    )
                assert "offset" in str(exc_info.value)
                assert "ge=0" in str(exc_info.value).lower() or "greater than or equal to 0" in str(exc_info.value).lower()
            finally:
                await Tortoise.close_connections()

        asyncio.run(run_test())
