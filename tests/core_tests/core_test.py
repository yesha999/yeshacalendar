import pytest

from core.models import User


@pytest.mark.django_db
def test_signup(client):
    data = {"username": "test", "first_name": "Test", "last_name": "Testov", "email": "Test@test.ru",
            "password": "Test12345", "password_repeat": "Test12345"}
    expected_data = {"username": "test", "first_name": "Test", "last_name": "Testov", "email": "Test@test.ru"}
    response = client.post(
        "/core/signup",
        data=data,
        content_type="application/json")
    assert response.status_code == 201
    assert response.data == expected_data


@pytest.mark.django_db
def test_login(client):
    User.objects.create_user(username="test_login", password="Test12345",
                             email="test@test.test")
    response = client.post(
        "/core/login",
        data={"username": "test_login", "password": "Test12345"},
        content_type="application/json")
    assert response.status_code == 200
    assert response.data["username"] == "test_login"


@pytest.mark.django_db
def test_logout(client, create_user):
    client.force_login(create_user)
    response = client.delete("/core/profile")
    assert response.status_code == 200
