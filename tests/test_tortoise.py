import asyncio
from tortoise import Tortoise, fields, models

from paginator.paginator import paginate


class User(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100)

    class Meta:
        table = "users"


def test_tortoise_pagination():
    """Test pagination with Tortoise ORM backend."""

    async def run_test():
        # Initialize Tortoise ORM with module path string
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
