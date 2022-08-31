from django.conf import settings
from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import Message
from goals.models import Goal, Board, BoardParticipant, GoalCategory


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient(settings.BOT_TOKEN)

    def send_goals(self, message: Message, tg_user: TgUser):
        goals = Goal.objects.filter(user=tg_user.user)
        if goals:
            goals_message = "\n".join([f"{goal.id}) {goal.title} "
                                       f"http://yeshacalendar.ga/categories/goals?goal={goal.id}" for goal in goals])
            self.tg_client.send_message(message.chat.id, goals_message)
        else:
            self.tg_client.send_message(message.chat.id, "Нет целей, /create для создания")

    def create_goal(self, message: Message, board_title, category_title):
        tg_user = TgUser.objects.get(tg_user_id=message.from_.id)
        category = GoalCategory.objects.filter(board__title=board_title, title=category_title, user=tg_user.user,
                                               board__participants__role__in=[BoardParticipant.Role.owner,
                                                                              BoardParticipant.Role.writer]).first()
        goal = Goal.objects.create(title=message.text, user=tg_user.user, category=category)
        self.tg_client.send_message(
            message.chat.id, f"Цель {goal.title} создана!,"
                             f" подробнее: http://yeshacalendar.ga/categories/goals?goal={goal.id}")

    def send_goal_name_question(self, message: Message, board_title):
        tg_user = TgUser.objects.get(tg_user_id=message.from_.id)
        board = Board.objects.filter(is_deleted=False, title=board_title, participants__user=tg_user.user).first()
        category = GoalCategory.objects.filter(board=board, title=message.text, user=tg_user.user).first()
        if not category:
            category = GoalCategory.objects.create(
                board=board, title=message.text, user=tg_user.user)

        self.tg_client.send_message(
            message.chat.id, f"Выбрана доска {board_title}, категория {category.title}, укажите название цели")

    def send_categories(self, message: Message):
        tg_user = TgUser.objects.get(tg_user_id=message.from_.id)
        board = Board.objects.filter(title=message.text, participants__user=tg_user.user, is_deleted=False).first()
        if not board:
            board = Board.objects.create(title=message.text)  # Создали или получили доску
            BoardParticipant.objects.create(user=tg_user.user, board=board, role=BoardParticipant.Role.owner)
        categories = GoalCategory.objects.filter(board=board, is_deleted=False)
        self.tg_client.send_message(message.chat.id, "Напишите название категории (если такой нет, будет создана новая)")
        if categories:
            self.tg_client.send_message(message.chat.id,
                                        '\n'.join([f"{category.id}) {category.title}" for category in categories]))
        else:
            self.tg_client.send_message(message.chat.id, "Существующих категорий не найдено")

    def send_boards(self, message: Message, tg_user: TgUser):
        boards = Board.objects.filter(participants__user=tg_user.user, is_deleted=False)
        self.tg_client.send_message(message.chat.id, "Напишите название доски (если такой нет, будет создана новая)")
        if boards:
            self.tg_client.send_message(message.chat.id, '\n'.join([f"{board.id}) {board.title}" for board in boards]))
        else:
            self.tg_client.send_message(message.chat.id, "Существующих досок не найдено")

    def handle_user_message(self, message: Message, tg_user: TgUser):
        if "/goals" in message.text:
            self.send_goals(message, tg_user)
        elif "/create" in message.text:
            self.send_boards(message, tg_user)
        elif "/cancel" in message.text:
            self.tg_client.send_message(message.chat.id, "Вернулись в начало")
        else:
            self.tg_client.send_message(message.chat.id, "Неизвестная команда")

    def handle_verification_message(self, message: Message, tg_user: TgUser):
        tg_user.set_verification_code()
        tg_user.save(update_fields=["verification_code"])
        self.tg_client.send_message(message.chat.id, tg_user.verification_code)

    def handle_message(self, message: Message):
        tg_user, created = TgUser.objects.get_or_create(
            tg_user_id=message.from_.id, defaults={"tg_chat_id": message.chat.id,
                                                   "tg_username": message.from_.username})
        if created:
            self.tg_client.send_message(message.chat.id, "приветствую в yeshacalendar")
        if tg_user.user is None:
            self.handle_verification_message(message, tg_user)
        else:
            self.handle_user_message(message, tg_user)

    def handle(self, *args, **options):
        condition = "start"
        offset = 0
        board_title = "default_title"
        category_title = "default_title"
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                if item.message.text == "/create" \
                        and item.message.from_.username in \
                        [user.tg_username for user in TgUser.objects.all()]:  # Нужно для безошибочной работы,
                    # если неверифицированный пользователь написал /create
                    condition = "create1"  # состояние ожидания названия доски
                    self.handle_message(item.message)
                    continue
                if item.message.text == "/cancel":
                    condition = "start"
                if condition == "start":
                    self.handle_message(item.message)
                elif condition == "create1":  # Пользователь отправляет название доски
                    self.send_categories(item.message)
                    board_title = item.message.text  # запомнить для создания категории
                    condition = "create2"  # Состояние ожидания названия категории
                    continue
                elif condition == "create2":  # Пользователь отправляет название категории
                    self.send_goal_name_question(item.message, board_title)
                    category_title = item.message.text  # запомнить для создания цели
                    condition = "create3"  # Состояние ожидания названия цели
                    continue
                elif condition == "create3":
                    self.create_goal(item.message, board_title, category_title)
                    condition = "start"
