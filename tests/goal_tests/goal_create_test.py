import pytest

from goals.models import Goal


@pytest.mark.django_db
def test_board_create(client, csrf_token):
    header = {"X-CSRFToken": csrf_token}
    data = {"title": "test board title"}
    post_response = client.post("/goals/board/create", data=data, content_type="application/json",
                                headers=header)
    get_response = client.get(f"/goals/board/{post_response.data['id']}", headers=header)
    assert post_response.status_code == 201
    assert get_response.status_code == 200
    assert post_response.data["title"] == data["title"]
    assert get_response.data["title"] == data["title"]


@pytest.mark.django_db
def test_goal_category_create(client, csrf_token):
    header = {"X-CSRFToken": csrf_token}

    create_board = client.post("/goals/board/create", data={"title": "test board title"},
                               content_type="application/json", headers=header)

    data = {"title": "test category name", "board": create_board.data["id"]}

    expected_response = {'id': 1, 'title': data["title"], "board": data["board"], 'user': {"id": 2, "username": "test"}}

    post_response = client.post("/goals/goal_category/create", data=data, content_type="application/json",
                                headers=header)

    get_response = client.get(f"/goals/goal_category/{post_response.data['id']}", headers=header)

    assert post_response.status_code == 201
    assert post_response.data["title"] == expected_response["title"]
    assert post_response.data["board"] == expected_response["board"]
    assert get_response.status_code == 200
    assert get_response.data["user"]["username"] == expected_response["user"]["username"]
    assert get_response.data["title"] == expected_response["title"]
    assert get_response.data["board"] == expected_response["board"]


@pytest.mark.django_db
def test_goal_create(client, csrf_token):
    header = {"X-CSRFToken": csrf_token}
    create_board = client.post("/goals/board/create", data={"title": "test board title"},
                               content_type="application/json", headers=header)
    create_category = client.post("/goals/goal_category/create",
                                  data={"title": "test category name", "board": create_board.data["id"]},
                                  content_type="application/json",
                                  headers=header)
    data = {"category": create_category.data["id"], "title": "test goal title", "status": Goal.Status.to_do,
            "priority": Goal.Priority.medium, "due_date": "2024-08-17"}
    expected_data = {"category": create_category.data["id"], "title": "test goal title", "status": Goal.Status.to_do,
                     "priority": Goal.Priority.medium, "due_date": "2024-08-17", "description": None, "id": 1}
    post_response = client.post("/goals/goal/create", data=data, content_type="application/json",
                                headers=header)

    get_response = client.get(f"/goals/goal/{post_response.data['id']}", headers=header)

    post_response_data = post_response.data
    post_response_data.pop("created", None)
    post_response_data.pop("updated", None)

    assert post_response.status_code == 201
    assert post_response_data == expected_data
    assert get_response.status_code == 200
    assert get_response.data["user"]["username"] == "test"
    assert get_response.data["title"] == data["title"]
    assert get_response.data["status"] == data["status"]

