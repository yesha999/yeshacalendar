import pytest

from core.serialzers import User


@pytest.fixture
@pytest.mark.django_db
def csrf_token(client, django_user_model: User):
    django_user_model.objects.create_user(username="test", password="Test1234",
                                          email="test@test.test")
    response = client.post(
        "/core/login",
        data={"username": "test", "password": "Test1234"},
        content_type="application/json")
    return response.cookies['csrftoken']