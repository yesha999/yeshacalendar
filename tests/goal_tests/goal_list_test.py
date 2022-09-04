import pytest

from core.models import User
from goals.models import BoardParticipant, Goal


@pytest.mark.django_db
class TestList:

    def test_board_list(self, client, header: dict, boards_count: int = 5):
        for i in range(boards_count):
            title = f"test board title{i}"
            post_response = client.post("/goals/board/create", data={"title": title},
                                        content_type="application/json", headers=header)
        get_response = client.get(f"/goals/board/list", headers=header)

        assert get_response.status_code == 200
        assert len(get_response.data) == boards_count
        assert get_response.data[0]["title"] == 'test board title0'
        assert get_response.data[1]["title"] == 'test board title1'

    @pytest.mark.parametrize("boards_count,limit", [(10, 5), (3, 2), (15, 25), (10, 10), (25, 3)])
    def test_board_list_limit_offset(self, client, header: dict, boards_count, limit):
        for i in range(boards_count):
            title = f"test board title{i}"
            post_response = client.post("/goals/board/create", data={"title": title},
                                        content_type="application/json", headers=header)
        get_response = client.get(f"/goals/board/list?limit={limit}", headers=header)
        assert len(get_response.data["results"]) == limit if boards_count >= limit else boards_count  # Тест лимитов

        pages_count = boards_count // limit
        if boards_count % limit != 0:
            pages_count = boards_count // limit + 1
        last_page_offset = (pages_count - 1) * limit

        get_response = client.get(f"/goals/board/list?limit={limit}&offset={last_page_offset}", headers=header)

        assert len(get_response.data["results"]) == boards_count - limit * (pages_count - 1)  # Тест лимитов и оффсетов

    def test_board_list_by_participant(self, client, header: dict, boards_count: int = 5):
        participant = User.objects.create_user(username="board_participant", password="Test1234",
                                               email="test@test.test")  # создаем дополнительного юзера
        for i in range(boards_count):
            title = f"test board title{i}"
            post_response = client.post("/goals/board/create", data={"title": title},
                                        content_type="application/json", headers=header)
            if i != 0:  # Чтобы не все созданные доски были общими у создателя и редактора
                update_response = client.put(
                    f"/goals/board/{post_response.data['id']}",
                    data={"title": title, "participants": [
                        {"role": BoardParticipant.Role.writer, "user": participant.username}]},
                    content_type="application/json", headers=header)

        logout = client.delete("/core/profile", headers=header)
        relogin = client.post(
            "/core/login",
            data={"username": participant.username, "password": "Test1234"},
            content_type="application/json")
        relogin_token = relogin.cookies['csrftoken']
        header_relogin = {"X-CSRFToken": relogin_token}

        get_response = client.get(f"/goals/board/list", headers=header_relogin)

        assert get_response.status_code == 200
        assert len(get_response.data) == boards_count - 1
        assert get_response.data[0]["title"] == 'test board title1'
        assert get_response.data[1]["title"] == 'test board title2'

    def test_goal_category_list(self, client, header: dict, categories_count: int = 3):
        board_create = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json", headers=header)
        for i in range(categories_count):
            category_title = f"test category title{i}"
            data = {"title": category_title, "board": board_create.data["id"]}
            category_create = client.post("/goals/goal_category/create", data=data, content_type="application/json",
                                          headers=header)

        get_response = client.get(f"/goals/goal_category/list", headers=header)

        assert get_response.status_code == 200
        assert len(get_response.data) == categories_count
        assert get_response.data[0]["title"] == 'test category title0'
        assert get_response.data[1]["title"] == 'test category title1'
        assert get_response.data[1]["board"] == board_create.data["id"]

    def test_goal_category_list_ordering(self, client, header: dict, categories_count: int = 3):
        board_create = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json", headers=header)
        for i in range(categories_count):
            category_title = f"test category title{i}"
            data = {"title": category_title, "board": board_create.data["id"]}
            category_create = client.post("/goals/goal_category/create", data=data, content_type="application/json",
                                          headers=header)
        category_create = client.post("/goals/goal_category/create",
                                      data={"title": "a title", "board": board_create.data["id"]},
                                      # Чтобы начиналось на а
                                      content_type="application/json",
                                      headers=header)
        get_response = client.get(f"/goals/goal_category/list?ordering=title", headers=header)

        assert get_response.data[0]["title"] == "a title"

    def test_goal_list(self, client, header: dict, goals_count: int = 3):
        board_create = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json", headers=header)
        category_data = {"title": "category_title", "board": board_create.data["id"]}
        category_create = client.post("/goals/goal_category/create", data=category_data,
                                      content_type="application/json", headers=header)

        for i in range(goals_count):
            goal_title = f"test goal title{i}"
            data = {"category": category_create.data["id"], "title": goal_title, "status": Goal.Status.to_do,
                    "priority": Goal.Priority.medium, "due_date": "2024-08-17"}

            goal_create = client.post("/goals/goal/create", data=data, content_type="application/json",
                                      headers=header)

        get_response = client.get(f"/goals/goal/list", headers=header)

        assert get_response.status_code == 200
        assert len(get_response.data) == goals_count
        assert get_response.data[0]["title"] == 'test goal title0'
        assert get_response.data[1]["title"] == 'test goal title1'
        assert get_response.data[0]["due_date"] == "2024-08-17"
        assert get_response.data[1]["category"] == category_create.data["id"]

    def test_goal_list_2_categories(self, client, header: dict, goals_count: int = 3):
        board_create = client.post("/goals/board/create", data={"title": "test board title"},
                                   content_type="application/json", headers=header)
        category_data = {"title": "category_title", "board": board_create.data["id"]}
        category_create = client.post("/goals/goal_category/create", data=category_data,
                                      content_type="application/json", headers=header)

        for i in range(goals_count):
            goal_title = f"test goal title{i}"
            data = {"category": category_create.data["id"], "title": goal_title, "status": Goal.Status.to_do,
                    "priority": Goal.Priority.medium, "due_date": "2024-08-17"}

            goal_create = client.post("/goals/goal/create", data=data, content_type="application/json",
                                      headers=header)

        second_category_create = client.post("/goals/goal_category/create",
                                             data={"title": "second_category_title", "board": board_create.data["id"]},
                                             content_type="application/json", headers=header)
        goal_create = client.post("/goals/goal/create", data={"category": second_category_create.data["id"],
                                                              "title": "sec cat title", "status": Goal.Status.to_do,
                                                              "priority": Goal.Priority.medium,
                                                              "due_date": "2024-08-17"},
                                  content_type="application/json",
                                  headers=header)

        get_response1 = client.get(f"/goals/goal/list?category__in={category_create.data['id']}", headers=header)
        get_response2 = client.get(f"/goals/goal/list?category__in={second_category_create.data['id']}", headers=header)
        assert get_response1.data[0]["title"] == 'test goal title0'
        assert get_response2.data[0]["title"] == "sec cat title"
