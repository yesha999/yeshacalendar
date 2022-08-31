import random

from django.db import models

from core.models import User
from goals.models import Board, GoalCategory

SYMBOLS = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM12345678901234567890"  # Цифры 2 раза для того,
# чтобы чаще попадались, так коды верификации выглядят красивее


class TgUser(models.Model):
    class Meta:
        verbose_name = "Телеграм Юзер"
        verbose_name_plural = "Телеграм Юзеры"

    class Condition(models.IntegerChoices):
        create1 = 1, "Ожидание названия доски"
        create2 = 2, "Ожидание названия категории"
        create3 = 3, "Ожидание названия цели"
        start = 4, "Начало"

    tg_chat_id = models.BigIntegerField(verbose_name="Телеграм чат id")
    tg_user_id = models.BigIntegerField(verbose_name="Телеграм юзер id", unique=True)
    tg_username = models.CharField(
        max_length=512, verbose_name="Телеграм username", null=True, blank=True, default=None
    )
    user = models.ForeignKey(User, verbose_name="Связанный пользователь", on_delete=models.PROTECT, null=True,
                             blank=True, default=None)
    verification_code = models.CharField(max_length=5, null=True, blank=True, default=None,
                                         verbose_name="Код подтверждения")
    bot_condition = models.PositiveSmallIntegerField(verbose_name="Состояние бота", choices=Condition.choices,
                                                     default=Condition.start)

    active_board = models.ForeignKey(Board, verbose_name="Поле доски для создания категории", on_delete=models.PROTECT,
                                     null=True, blank=True, default=None) #  поле нужно для того,
    # чтобы запомнить в процессе исполнения бота в какую доску класть создаваемую цель (категорию)
    active_category = models.ForeignKey(GoalCategory, verbose_name="Поле категории для создания цели",
                                        on_delete=models.PROTECT, null=True, blank=True, default=None)  # см. выше

    def set_verification_code(self):
        self.verification_code = "".join([random.choice(SYMBOLS) for i in range(5)])
