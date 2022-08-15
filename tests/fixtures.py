import pytest

from tests.factories import UserFactory


@pytest.fixture
@pytest.mark.django_db
def csrf_token(client, django_user_model):
    user = UserFactory.create()  # на этом этапе создается юзер с id = 1, поэтому в тестах мы будем ожидать user с id = 2
    django_user_model.objects.create_user(username="test", password=user.password,
                                          email="test@test.test")  # здесь создается user с id = 2
    response = client.post(
        "/core/login",
        data={"username": "test", "password": user.password},
        content_type="application/json")
    return response.cookies['csrftoken']
