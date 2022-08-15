import pytest


@pytest.mark.django_db
def test_goal_category_create(client, csrf_token):
    data = {"title": "test category name"}

    expected_response = {'id': 1, 'title': data["title"], 'user': 2}

    post_response = client.post("/goals/goal_category/create", data=data, content_type="application/json",
                           headers={'X-CSRFToken': csrf_token})

    get_response = client.get("/goals/goal_category/list", headers={'X-CSRFToken': csrf_token})
    print(get_response)

    assert post_response.status_code == 201
    assert post_response.data["title"] == expected_response["title"]
    assert get_response.data[0]["user"] == expected_response["user"]
    assert get_response.data[0]["title"] == expected_response["title"]
