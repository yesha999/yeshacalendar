import random

from django.db import models

from core.models import User

SYMBOLS = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM12345678901234567890"


class TgUser(models.Model):
    class Meta:
        verbose_name = "Телеграм Юзер"
        verbose_name_plural = "Телеграм Юзеры"

    tg_chat_id = models.BigIntegerField(verbose_name="Телеграм чат id")
    tg_user_id = models.BigIntegerField(verbose_name="Телеграм юзер id", unique=True)
    tg_username = models.CharField(
        max_length=512, verbose_name="Телеграм username", null=True, blank=True, default=None
    )
    user = models.ForeignKey(User, verbose_name="Связанный пользователь", on_delete=models.PROTECT, null=True,
                             blank=True, default=None)
    verification_code = models.CharField(max_length=5, null=True, blank=True, default=None,
                                         verbose_name="Код подтверждения")

    def set_verification_code(self):
        self.verification_code = "".join([random.choice(SYMBOLS) for i in range(5)])
