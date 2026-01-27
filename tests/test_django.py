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

from paginator.paginator import paginate_sync


class User(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "tests"


def test_django_pagination():
    with connection.schema_editor() as schema:
        schema.create_model(User)

    User.objects.bulk_create(
        [User(name=f"user{i}") for i in range(50)]
    )

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
