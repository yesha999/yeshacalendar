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
        """
        Функция отправит в тг список текущих целей и ссылки на них.
        :param message:
        :param tg_user:
        """
        goals = Goal.objects.filter(
            category__board__participants__user=tg_user.user, status__in=[Goal.Status.to_do, Goal.Status.in_progress])
        if goals:
            goals_message = "\n".join([f"{goal.title} "
                                       f"http://yeshacalendar.ga/categories/goals?goal={goal.id}" for goal in goals])
            self.tg_client.send_message(message.chat.id, goals_message)
        else:
            self.tg_client.send_message(message.chat.id, "Нет целей, /create для создания")

    def create_goal(self, message: Message, tg_user: TgUser):
        """
        Функция создаст цель с указанным названием, остальные параметры останутся дефолтными.
        :param message:
        :param tg_user:
        """
        goal = Goal.objects.create(title=message.text, user=tg_user.user, category=tg_user.active_category)
        self.tg_client.send_message(
            message.chat.id, f"Цель {goal.title} создана!,"
                             f" подробнее: http://yeshacalendar.ga/categories/goals?goal={goal.id}")

    def send_goal_name_question(self, message: Message, tg_user: TgUser):
        """
        После передачи названия категории, функция найдет или создаст объект категории
        и положит его в БД, далее отправится сообщение с предложением написать название цели.
        :param message:
        :param tg_user:
        """
        category = GoalCategory.objects.filter(
            board=tg_user.active_board, title=message.text, user=tg_user.user,
            board__participants__role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]).first()
        if not category:
            category = GoalCategory.objects.create(
                board=tg_user.active_board, title=message.text, user=tg_user.user)
        tg_user.active_category = category
        tg_user.save(update_fields=["active_category"])
        self.tg_client.send_message(
            message.chat.id, f"Выбрана доска {tg_user.active_board.title}, категория {category.title},"
                             f" укажите название цели")

    def send_categories(self, message: Message, tg_user: TgUser):
        """
        Функция получит или создаст объект доски с указанным названием,
        запомнит его в БД для дальнейшего использования при создании категории,
        затем предложит список принадлежащих доске категорий для выбора.
        :param message:
        :param tg_user:
        """
        board = Board.objects.filter(title=message.text, participants__user=tg_user.user, is_deleted=False).first()
        if not board:
            board = Board.objects.create(title=message.text)  # Создали или получили доску
            BoardParticipant.objects.create(user=tg_user.user, board=board, role=BoardParticipant.Role.owner)
        tg_user.active_board = board
        tg_user.save(update_fields=["active_board"])
        categories = GoalCategory.objects.filter(board=board, is_deleted=False)
        self.tg_client.send_message(message.chat.id,
                                    "Напишите название категории (если такой нет, будет создана новая)")
        if categories:
            self.tg_client.send_message(message.chat.id,
                                        '\n'.join([f"{category.title}" for category in categories]))
        else:
            self.tg_client.send_message(message.chat.id, "Существующих категорий не найдено")

    def send_boards(self, message: Message, tg_user: TgUser):
        """
        Функция отправит пользователю список досок (в случае их наличия), в которых он является участником.
        :param message:
        :param tg_user:
        """
        boards = Board.objects.filter(participants__user=tg_user.user, is_deleted=False)
        self.tg_client.send_message(message.chat.id, "Напишите название доски (если такой нет, будет создана новая)")
        if boards:
            self.tg_client.send_message(message.chat.id, '\n'.join([f"{board.title}" for board in boards]))
        else:
            self.tg_client.send_message(message.chat.id, "Существующих досок не найдено")

    def handle_user_message(self, message: Message, tg_user: TgUser):
        """
        Функция смотрит сообщение пользователя, выводит дальнейшие действия в зависимости от сообщения,
        также функция отдает в БД текущее состояние бота по схеме состояний
         для определения на каком этапе создания цели находится пользователь.
        :param message:
        :param tg_user:
        """
        if tg_user.bot_condition == TgUser.Condition.start:
            if "/goals" in message.text:
                self.send_goals(message, tg_user)
            elif "/create" in message.text:
                tg_user.bot_condition = TgUser.Condition.create1
                self.send_boards(message, tg_user)
            else:
                self.tg_client.send_message(message.chat.id, "Неизвестная команда")
        elif tg_user.bot_condition != TgUser.Condition.start and "/cancel" in message.text:
            tg_user.bot_condition = TgUser.Condition.start
            self.tg_client.send_message(message.chat.id, "Вернулись в начало")
        elif tg_user.bot_condition == TgUser.Condition.create1:
            self.send_categories(message, tg_user)
            tg_user.bot_condition = TgUser.Condition.create2  # Состояние ожидания названия категории
        elif tg_user.bot_condition == TgUser.Condition.create2:
            self.send_goal_name_question(message, tg_user)
            tg_user.bot_condition = TgUser.Condition.create3  # Состояние ожидания названия цели
        elif tg_user.bot_condition == TgUser.Condition.create3:
            self.create_goal(message, tg_user)
            tg_user.bot_condition = TgUser.Condition.start
        tg_user.save(update_fields=["bot_condition"])

    def handle_verification_message(self, message: Message, tg_user: TgUser):
        """
        Функция отправляет код верификации для неверифицированных пользователей.
        :param message:
        :param tg_user:
        """
        tg_user.set_verification_code()
        tg_user.save(update_fields=["verification_code"])
        self.tg_client.send_message(
            message.chat.id, f"Пожалуйста, пройдите верификацию на нашем сайте"
                             f" http://yeshacalendar.ga,\nКод подтверждения: {tg_user.verification_code}")

    def handle_message(self, message: Message):
        """
        Функция получает или создает объект ТГ юзера в зависимости от кого пришло сообщение в апдейте,
         выявляет верифицирован юзер или нет, в зависимости от этого определяет дальнейшие действия.
        :param message:
        :return:
        """
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
        """
        Функция в бесконечном цикле создает оповещения о новых сообщениях юзеров,
         для каждого нового сообщения передается ответ в зависимости от инструкций функции self.handle_message
        :param args:
        :param options:
        """
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)
