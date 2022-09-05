import pytest

from core.models import User


@pytest.fixture
def create_user(django_user_model: User):
    user = django_user_model.objects.create_user(username="test", password="Test1234",
                                                 email="test@test.test")
    return user
