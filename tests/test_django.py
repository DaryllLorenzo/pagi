import django
from django.conf import settings

settings.configure(
    INSTALLED_APPS=["django.contrib.contenttypes"],
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    },
)
django.setup()

from django.db import models, connection
from pydantic import ValidationError
import pytest

from paginator.paginator import paginate_sync


class User(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "tests"


# Create table once at module load
with connection.schema_editor() as schema:
    schema.create_model(User)


def test_django_pagination():
    User.objects.bulk_create([User(name=f"user{i}") for i in range(50)])

    result = paginate_sync(
        connection=None,
        query_func=lambda: User.objects.all(),
        offset=20,
        limit=10,
        backend="django",
    )

    assert result.total == 50
    assert result.offset == 20
    assert result.limit == 10
    assert len(result.items) == 10
    assert result.items[0].name == "user20"


class TestDjangoEdgeCases:
    """Edge case tests for Django ORM backend."""

    def setup_method(self):
        User.objects.all().delete()

    def test_empty_result_set(self):
        """Query returns 0 records."""
        result = paginate_sync(
            connection=None,
            query_func=lambda: User.objects.all(),
            offset=0,
            limit=10,
            backend="django",
        )
        assert result.total == 0
        assert result.offset == 0
        assert result.limit == 10
        assert len(result.items) == 0

    def test_first_page(self):
        """First page with offset=0, limit=N."""
        User.objects.bulk_create([User(name=f"user{i}") for i in range(30)])

        result = paginate_sync(
            connection=None,
            query_func=lambda: User.objects.all(),
            offset=0,
            limit=10,
            backend="django",
        )
        assert result.total == 30
        assert result.offset == 0
        assert result.limit == 10
        assert len(result.items) == 10
        assert result.items[0].name == "user0"

    def test_last_page_partial(self):
        """Last page where limit exceeds remaining records."""
        User.objects.bulk_create([User(name=f"user{i}") for i in range(25)])

        result = paginate_sync(
            connection=None,
            query_func=lambda: User.objects.all(),
            offset=20,
            limit=10,
            backend="django",
        )
        assert result.total == 25
        assert result.offset == 20
        assert result.limit == 10
        assert len(result.items) == 5
        assert result.items[0].name == "user20"
        assert result.items[-1].name == "user24"

    def test_exact_page_boundary(self):
        """Exact page boundary where offset + limit == total."""
        User.objects.bulk_create([User(name=f"user{i}") for i in range(30)])

        result = paginate_sync(
            connection=None,
            query_func=lambda: User.objects.all(),
            offset=20,
            limit=10,
            backend="django",
        )
        assert result.total == 30
        assert result.offset == 20
        assert result.limit == 10
        assert len(result.items) == 10
        assert result.items[0].name == "user20"
        assert result.items[-1].name == "user29"

    def test_offset_beyond_total(self):
        """Offset > total should return empty items."""
        User.objects.bulk_create([User(name=f"user{i}") for i in range(30)])

        result = paginate_sync(
            connection=None,
            query_func=lambda: User.objects.all(),
            offset=50,
            limit=10,
            backend="django",
        )
        assert result.total == 30
        assert result.offset == 50
        assert result.limit == 10
        assert len(result.items) == 0

    def test_maximum_limit(self):
        """Test with limit=100 (the configured maximum)."""
        User.objects.bulk_create([User(name=f"user{i}") for i in range(150)])

        result = paginate_sync(
            connection=None,
            query_func=lambda: User.objects.all(),
            offset=0,
            limit=100,
            backend="django",
        )
        assert result.total == 150
        assert result.offset == 0
        assert result.limit == 100
        assert len(result.items) == 100

    def test_limit_zero_validation_error(self):
        """limit=0 should raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            paginate_sync(
                connection=None,
                query_func=lambda: User.objects.all(),
                offset=0,
                limit=0,
                backend="django",
            )
        assert "limit" in str(exc_info.value)
        assert "gt=0" in str(exc_info.value).lower() or "greater than 0" in str(exc_info.value).lower()

    def test_limit_exceeds_maximum(self):
        """limit > 100 should raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            paginate_sync(
                connection=None,
                query_func=lambda: User.objects.all(),
                offset=0,
                limit=101,
                backend="django",
            )
        assert "limit" in str(exc_info.value)
        assert "le=100" in str(exc_info.value).lower() or "less than or equal to 100" in str(exc_info.value).lower()

    def test_negative_offset_validation_error(self):
        """Negative offset should raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            paginate_sync(
                connection=None,
                query_func=lambda: User.objects.all(),
                offset=-5,
                limit=10,
                backend="django",
            )
        assert "offset" in str(exc_info.value)
        assert "ge=0" in str(exc_info.value).lower() or "greater than or equal to 0" in str(exc_info.value).lower()
