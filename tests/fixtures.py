import pytest

from core.models import User


@pytest.fixture
def header(client, django_user_model: User):
    django_user_model.objects.create_user(username="test", password="Test1234",
                                          email="test@test.test")
    response = client.post(
        "/core/login",
        data={"username": "test", "password": "Test1234"},
        content_type="application/json")
    return {"X-CSRFToken": response.cookies['csrftoken']}
