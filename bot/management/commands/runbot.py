from django.conf import settings
from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import Message
from goals.models import Goal


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient(settings.BOT_TOKEN)

    def send_goals(self, message: Message, tg_user: TgUser):
        goals = Goal.objects.filter(user=tg_user.user)
        if goals:
            goals_message = "\n".join([f"{goal.id}) {goal.title}" for goal in goals])
            self.tg_client.send_message(message.chat.id, goals_message)
        else:
            self.tg_client.send_message(message.chat.id, "Нет целей, /create для создания")

    def send_boards(self, message: Message, tg_user: TgUser):
        self.tg_client.send_message(message.chat.id, "пока создание недоступно, в разработке")

    def handle_user_message(self, message: Message, tg_user: TgUser):
        if "/goals" in message.text:
            self.send_goals(message, tg_user)
        elif "/create" in message.text:
            self.send_boards(message, tg_user)
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
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)
