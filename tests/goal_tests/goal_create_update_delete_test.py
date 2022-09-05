import pytest

from core.models import User
from goals.models import Goal, BoardParticipant


@pytest.mark.django_db
class TestCreateUpdateDelete:

    def test_board_create(self, client, create_user):
        client.force_login(create_user)
        data = {"title": "test board title"}
        post_response = client.post("/goals/board/create", data=data, content_type="application/json")
        get_response = client.get(f"/goals/board/{post_response.data['id']}")
        assert post_response.status_code == 201
        assert get_response.status_code == 200
        assert post_response.data["title"] == data["title"]
        assert get_response.data["title"] == data["title"]

    def test_board_update(self, client, create_user):
        client.force_login(create_user)
        create_board = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json")  # создаем доску
        participant = User.objects.create_user(username="board_participant", password="Test1234",
                                               email="test@test.test")  # создаем юзера для проверки
        # дополнения участников
        update_response = client.put(
            f"/goals/board/{create_board.data['id']}",
            data={"title": "test board title updated", "participants": [
                {"role": BoardParticipant.Role.writer, "user": participant.username}]},
            content_type="application/json")

        assert update_response.status_code == 200
        assert update_response.data["title"] == "test board title updated"
        assert update_response.data["participants"][-1]["user"] == participant.username

    def test_board_detail_by_participant(self, client, create_user):
        client.force_login(create_user)
        create_board = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json")  # создаем доску
        participant = User.objects.create_user(username="board_participant", password="Test1234",
                                               email="test@test.test")  # создаем юзера для
        # проверки дополнения участников
        update_response = client.put(
            f"/goals/board/{create_board.data['id']}",
            data={"title": "test board title updated", "participants": [
                {"role": BoardParticipant.Role.writer, "user": participant.username}]},
            content_type="application/json")
        client.force_login(participant)  # Релогинимся
        get_by_participant = client.get(
            f"/goals/board/{create_board.data['id']}")

        assert get_by_participant.status_code == 200
        assert get_by_participant.data == update_response.data

    def test_board_update_not_owner(self, client, create_user):
        client.force_login(create_user)
        create_board = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json")  # создаем доску
        participant = User.objects.create_user(username="board_participant", password="Test1234",
                                               email="test@test.test")  # создаем юзера
        # для проверки дополнения участников
        update_response = client.put(
            f"/goals/board/{create_board.data['id']}",
            data={"title": "test board title updated", "participants": [
                {"role": BoardParticipant.Role.writer, "user": participant.username}]},
            content_type="application/json")
        client.force_login(participant)
        update_response_by_participant = client.put(
            f"/goals/board/{create_board.data['id']}",
            data={"title": "title updated 2", "participants": [
                {"role": BoardParticipant.Role.writer, "user": participant.username}]},
            content_type="application/json")
        assert update_response_by_participant.status_code == 403  # Доступно только владельцу

    def test_board_delete(self, client, create_user):
        client.force_login(create_user)
        create_board = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json")  # создаем доску
        delete_response = client.delete(f"/goals/board/{create_board.data['id']}")
        get_response = client.get(f"/goals/board/{create_board.data['id']}")
        assert delete_response.status_code == 204
        assert get_response.status_code == 404

    def test_board_delete_not_owner(self, client, create_user):
        client.force_login(create_user)
        create_board = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json")  # создаем доску
        not_owner_user = User.objects.create_user(username="board_participant", password="Test1234",
                                                  email="test@test.test")
        update_response = client.put(
            f"/goals/board/{create_board.data['id']}",
            data={"title": "test board title updated", "participants": [
                {"role": BoardParticipant.Role.writer, "user": not_owner_user.username}]},
            content_type="application/json")
        client.force_login(not_owner_user)
        delete_response = client.delete(f"/goals/board/{create_board.data['id']}")
        get_detail = client.get(f"/goals/board/{create_board.data['id']}")

        assert delete_response.status_code == 403
        assert get_detail.status_code == 200

    def test_goal_category_create(self, client, create_user):
        client.force_login(create_user)
        create_board = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json")
        data = {"title": "test category name", "board": create_board.data["id"]}
        expected_response = {'id': 1, 'title': data["title"], "board": data["board"],
                             'user': {"id": 2, "username": "test"}}
        post_response = client.post("/goals/goal_category/create", data=data, content_type="application/json")

        get_response = client.get(f"/goals/goal_category/{post_response.data['id']}")

        assert post_response.status_code == 201
        assert post_response.data["title"] == expected_response["title"]
        assert post_response.data["board"] == expected_response["board"]
        assert get_response.status_code == 200
        assert get_response.data["user"]["username"] == expected_response["user"]["username"]
        assert get_response.data["title"] == expected_response["title"]
        assert get_response.data["board"] == expected_response["board"]

    def test_goal_category_update(self, client, create_user):
        client.force_login(create_user)
        create_board = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json")
        data = {"title": "test category name", "board": create_board.data["id"]}
        post_response = client.post("/goals/goal_category/create", data=data, content_type="application/json")
        update_response = client.put(
            f"/goals/goal_category/{post_response.data['id']}",
            data={"title": "test category name updated"},
            content_type="application/json")

        assert update_response.data["title"] == "test category name updated"

    def test_goal_category_delete(self, client, create_user):
        client.force_login(create_user)
        create_board = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json")
        data = {"title": "test category name", "board": create_board.data["id"]}
        post_response = client.post("/goals/goal_category/create", data=data, content_type="application/json")
        delete_response = client.delete(
            f"/goals/goal_category/{post_response.data['id']}")

        assert delete_response.status_code == 204

    def test_goal_category_update_by_participant(self, client, create_user):
        client.force_login(create_user)
        create_board = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json")
        data = {"title": "test category name", "board": create_board.data["id"]}

        post_response = client.post("/goals/goal_category/create", data=data, content_type="application/json")

        not_owner_user = User.objects.create_user(username="board_participant", password="Test1234",
                                                  email="test@test.test")
        add_participant_to_board = client.put(
            f"/goals/board/{create_board.data['id']}",
            data={"title": "test board title updated", "participants": [
                {"role": BoardParticipant.Role.writer, "user": not_owner_user.username}]},
            content_type="application/json")
        client.force_login(not_owner_user)
        update_response = client.put(
            f"/goals/goal_category/{post_response.data['id']}",
            data={"title": "test category name updated"},
            content_type="application/json")

        assert update_response.status_code == 200
        assert update_response.data["title"] == "test category name updated"

    def test_goal_category_delete_by_participant(self, client, create_user):
        client.force_login(create_user)
        create_board = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json")
        data = {"title": "test category name", "board": create_board.data["id"]}
        post_response = client.post("/goals/goal_category/create", data=data, content_type="application/json")
        not_owner_user = User.objects.create_user(username="board_participant", password="Test1234",
                                                  email="test@test.test")
        add_participant_to_board = client.put(
            f"/goals/board/{create_board.data['id']}",
            data={"title": "test board title updated", "participants": [
                {"role": BoardParticipant.Role.writer, "user": not_owner_user.username}]},
            content_type="application/json")
        client.force_login(not_owner_user)
        delete_response = client.delete(
            f"/goals/goal_category/{post_response.data['id']}")

        assert delete_response.status_code == 204

    def test_goal_category_update_delete_by_participant_reader(self, client, create_user):
        client.force_login(create_user)
        create_board = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json")
        data = {"title": "test category name", "board": create_board.data["id"]}
        post_response = client.post("/goals/goal_category/create", data=data, content_type="application/json")

        not_owner_user = User.objects.create_user(username="board_participant", password="Test1234",
                                                  email="test@test.test")
        add_participant_to_board = client.put(
            f"/goals/board/{create_board.data['id']}",
            data={"title": "test board title updated", "participants": [
                {"role": BoardParticipant.Role.reader, "user": not_owner_user.username}]},
            content_type="application/json")
        client.force_login(not_owner_user)
        update_response = client.put(
            f"/goals/goal_category/{post_response.data['id']}",
            data={"title": "test category name updated"},
            content_type="application/json")
        delete_response = client.delete(
            f"/goals/goal_category/{post_response.data['id']}")

        assert update_response.status_code == 403
        assert delete_response.status_code == 403

    def test_goal_create(self, client, create_user):
        client.force_login(create_user)
        create_board = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json")
        create_category = client.post("/goals/goal_category/create",
                                      data={"title": "test category name", "board": create_board.data["id"]},
                                      content_type="application/json")
        data = {"category": create_category.data["id"], "title": "test goal title", "status": Goal.Status.to_do,
                "priority": Goal.Priority.medium, "due_date": "2024-08-17"}
        expected_data = {"category": create_category.data["id"], "title": "test goal title",
                         "status": Goal.Status.to_do,
                         "priority": Goal.Priority.medium, "due_date": "2024-08-17", "description": None, "id": 1}
        post_response = client.post("/goals/goal/create", data=data, content_type="application/json")

        get_response = client.get(f"/goals/goal/{post_response.data['id']}")

        post_response_data = post_response.data
        post_response_data.pop("created", None)
        post_response_data.pop("updated", None)  # Исключаем, т.к. не можем предсказать точное время создания сущностей

        assert post_response.status_code == 201
        assert post_response_data == expected_data
        assert get_response.status_code == 200
        assert get_response.data["user"]["username"] == "test"
        assert get_response.data["title"] == data["title"]
        assert get_response.data["status"] == data["status"]

    def test_goal_update_delete(self, client, create_user):
        client.force_login(create_user)
        create_board = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json")
        create_category = client.post("/goals/goal_category/create",
                                      data={"title": "test category name", "board": create_board.data["id"]},
                                      content_type="application/json")
        data = {"category": create_category.data["id"], "title": "test goal title", "status": Goal.Status.to_do,
                "priority": Goal.Priority.medium, "due_date": "2024-08-17"}

        post_response = client.post("/goals/goal/create", data=data, content_type="application/json")

        update_response = client.put(f"/goals/goal/{post_response.data['id']}",
                                     data={"title": "test update goal title", "status": Goal.Status.in_progress,
                                           "description": "new_description",
                                           "due_date": "2024-08-17", "priority": Goal.Priority.low,
                                           "category": create_category.data["id"]},
                                     content_type="application/json")

        expected_data = {"category": create_category.data["id"],
                         "title": "test update goal title", "status": Goal.Status.in_progress,
                         "priority": Goal.Priority.low, "due_date": "2024-08-17",
                         "description": "new_description", "id": 2}

        update_response_data = update_response.data
        update_response_data.pop("user", None)
        update_response_data.pop("created", None)
        update_response_data.pop("updated",
                                 None)  # Исключаем, т.к. не можем предсказать точное время создания сущностей

        delete_response = client.delete(f"/goals/goal/{post_response.data['id']}")

        assert post_response.status_code == 201
        assert update_response.status_code == 200
        assert update_response.data == expected_data
        assert delete_response.status_code == 204
