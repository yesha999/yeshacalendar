import pytest

from core.models import User
from goals.models import Goal, BoardParticipant


@pytest.mark.django_db
def test_board_create(client, csrf_token: str):
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
def test_board_update(client, csrf_token: str):
    header = {"X-CSRFToken": csrf_token}

    create_board = client.post("/goals/board/create", data={"title": "test board title"},
                               content_type="application/json", headers=header)  # создаем доску
    participant = User.objects.create_user(username="board_participant", password="Test1234",
                                           email="test@test.test")  # создаем юзера для проверки дополнения участников

    update_response = client.put(
        f"/goals/board/{create_board.data['id']}",
        data={"title": "test board title updated", "participants": [
            {"role": BoardParticipant.Role.writer, "user": participant.username}]},
        content_type="application/json", headers=header)

    logout = client.delete("/core/profile", headers=header)
    relogin = client.post(
        "/core/login",
        data={"username": participant.username, "password": "Test1234"},
        content_type="application/json")
    relogin_token = relogin.cookies['csrftoken']
    header_relogin = {"X-CSRFToken": relogin_token}

    get_by_participant = client.get(
        f"/goals/board/{create_board.data['id']}", headers=header_relogin)

    update_response_by_participant = client.put(
        f"/goals/board/{create_board.data['id']}",
        data={"title": "title updated 2", "participants": [
            {"role": BoardParticipant.Role.writer, "user": participant.username}]},
        content_type="application/json", headers=header_relogin)

    assert update_response.status_code == 200
    assert update_response.data["title"] == "test board title updated"
    assert update_response.data["participants"][-1]["user"] == participant.username
    assert get_by_participant.status_code == 200
    assert get_by_participant.data == update_response.data
    assert update_response_by_participant.status_code == 403


@pytest.mark.django_db
def test_board_delete(client, csrf_token: str):
    header = {"X-CSRFToken": csrf_token}
    create_board = client.post("/goals/board/create", data={"title": "test board title"},
                               content_type="application/json", headers=header)  # создаем доску

    delete_response = client.delete(f"/goals/board/{create_board.data['id']}", headers=header)
    get_response = client.get(f"/goals/board/{create_board.data['id']}", headers=header)
    assert delete_response.status_code == 204
    assert get_response.status_code == 404


@pytest.mark.django_db
def test_board_delete_not_owner(client, csrf_token: str):
    header = {"X-CSRFToken": csrf_token}
    create_board = client.post("/goals/board/create", data={"title": "test board title"},
                               content_type="application/json", headers=header)  # создаем доску

    not_owner_user = User.objects.create_user(username="board_participant", password="Test1234",
                                              email="test@test.test")

    update_response = client.put(
        f"/goals/board/{create_board.data['id']}",
        data={"title": "test board title updated", "participants": [
            {"role": BoardParticipant.Role.writer, "user": not_owner_user.username}]},
        content_type="application/json", headers=header)

    logout = client.delete("/core/profile", headers=header)
    relogin = client.post(
        "/core/login",
        data={"username": not_owner_user.username, "password": "Test1234"},
        content_type="application/json")
    relogin_token = relogin.cookies['csrftoken']
    header_relogin = {"X-CSRFToken": relogin_token}

    delete_response = client.delete(f"/goals/board/{create_board.data['id']}", headers=header_relogin)
    get_detail = client.get(f"/goals/board/{create_board.data['id']}", headers=header_relogin)

    assert delete_response.status_code == 403
    assert get_detail.status_code == 200


@pytest.mark.django_db
def test_goal_category_create(client, csrf_token: str):
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
def test_goal_category_update_delete(client, csrf_token: str):
    header = {"X-CSRFToken": csrf_token}

    create_board = client.post("/goals/board/create", data={"title": "test board title"},
                               content_type="application/json", headers=header)

    data = {"title": "test category name", "board": create_board.data["id"]}

    post_response = client.post("/goals/goal_category/create", data=data, content_type="application/json",
                                headers=header)

    update_response = client.put(
        f"/goals/goal_category/{post_response.data['id']}",
        data={"title": "test category name updated"},
        content_type="application/json", headers=header)

    delete_response = client.delete(
        f"/goals/goal_category/{post_response.data['id']}", headers=header)

    assert post_response.status_code == 201
    assert post_response.data["title"] == data["title"]
    assert post_response.data["board"] == data["board"]
    assert update_response.data["title"] == "test category name updated"
    assert delete_response.status_code == 204


@pytest.mark.django_db
def test_goal_category_update_delete_by_participant(client, csrf_token: str):
    header = {"X-CSRFToken": csrf_token}

    create_board = client.post("/goals/board/create", data={"title": "test board title"},
                               content_type="application/json", headers=header)

    data = {"title": "test category name", "board": create_board.data["id"]}

    post_response = client.post("/goals/goal_category/create", data=data, content_type="application/json",
                                headers=header)

    not_owner_user = User.objects.create_user(username="board_participant", password="Test1234",
                                              email="test@test.test")
    add_participant_to_board = client.put(
        f"/goals/board/{create_board.data['id']}",
        data={"title": "test board title updated", "participants": [
            {"role": BoardParticipant.Role.writer, "user": not_owner_user.username}]},
        content_type="application/json", headers=header)

    logout = client.delete("/core/profile", headers=header)
    relogin = client.post(
        "/core/login",
        data={"username": not_owner_user.username, "password": "Test1234"},
        content_type="application/json")
    relogin_token = relogin.cookies['csrftoken']
    header_relogin = {"X-CSRFToken": relogin_token}

    update_response = client.put(
        f"/goals/goal_category/{post_response.data['id']}",
        data={"title": "test category name updated"},
        content_type="application/json", headers=header_relogin)
    delete_response = client.delete(
        f"/goals/goal_category/{post_response.data['id']}", headers=header_relogin)

    assert update_response.status_code == 200
    assert update_response.data["title"] == "test category name updated"
    assert delete_response.status_code == 204


@pytest.mark.django_db
def test_goal_category_update_delete_by_participant_reader(client, csrf_token: str):
    header = {"X-CSRFToken": csrf_token}

    create_board = client.post("/goals/board/create", data={"title": "test board title"},
                               content_type="application/json", headers=header)

    data = {"title": "test category name", "board": create_board.data["id"]}

    post_response = client.post("/goals/goal_category/create", data=data, content_type="application/json",
                                headers=header)

    not_owner_user = User.objects.create_user(username="board_participant", password="Test1234",
                                              email="test@test.test")
    add_participant_to_board = client.put(
        f"/goals/board/{create_board.data['id']}",
        data={"title": "test board title updated", "participants": [
            {"role": BoardParticipant.Role.reader, "user": not_owner_user.username}]},
        content_type="application/json", headers=header)

    logout = client.delete("/core/profile", headers=header)
    relogin = client.post(
        "/core/login",
        data={"username": not_owner_user.username, "password": "Test1234"},
        content_type="application/json")
    relogin_token = relogin.cookies['csrftoken']
    header_relogin = {"X-CSRFToken": relogin_token}

    update_response = client.put(
        f"/goals/goal_category/{post_response.data['id']}",
        data={"title": "test category name updated"},
        content_type="application/json", headers=header_relogin)
    delete_response = client.delete(
        f"/goals/goal_category/{post_response.data['id']}", headers=header_relogin)

    assert update_response.status_code == 403
    assert delete_response.status_code == 403


@pytest.mark.django_db
def test_goal_create(client, csrf_token: str):
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
    post_response_data.pop("updated", None)  # Исключаем, т.к. не можем предсказать точное время создания сущностей

    assert post_response.status_code == 201
    assert post_response_data == expected_data
    assert get_response.status_code == 200
    assert get_response.data["user"]["username"] == "test"
    assert get_response.data["title"] == data["title"]
    assert get_response.data["status"] == data["status"]


@pytest.mark.django_db
def test_goal_update_delete(client, csrf_token: str):
    header = {"X-CSRFToken": csrf_token}
    create_board = client.post("/goals/board/create", data={"title": "test board title"},
                               content_type="application/json", headers=header)
    create_category = client.post("/goals/goal_category/create",
                                  data={"title": "test category name", "board": create_board.data["id"]},
                                  content_type="application/json", headers=header)
    data = {"category": create_category.data["id"], "title": "test goal title", "status": Goal.Status.to_do,
            "priority": Goal.Priority.medium, "due_date": "2024-08-17"}

    post_response = client.post("/goals/goal/create", data=data, content_type="application/json",
                                headers=header)

    update_response = client.put(f"/goals/goal/{post_response.data['id']}",
                                 data={"title": "test update goal title", "status": Goal.Status.in_progress,
                                       "description": "new_description",
                                       "due_date": "2024-08-17", "priority": Goal.Priority.low,
                                       "category": create_category.data["id"]},
                                 content_type="application/json", headers=header)

    expected_data = {"category": create_category.data["id"],
                     "title": "test update goal title", "status": Goal.Status.in_progress,
                     "priority": Goal.Priority.low, "due_date": "2024-08-17",
                     "description": "new_description", "id": 2}

    update_response_data = update_response.data
    update_response_data.pop("user", None)
    update_response_data.pop("created", None)
    update_response_data.pop("updated", None)  # Исключаем, т.к. не можем предсказать точное время создания сущностей

    delete_response = client.delete(f"/goals/goal/{post_response.data['id']}", headers=header)

    assert post_response.status_code == 201
    assert update_response.status_code == 200
    assert update_response.data == expected_data
    assert delete_response.status_code == 204
