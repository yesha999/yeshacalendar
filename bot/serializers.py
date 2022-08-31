from marshmallow import ValidationError
from rest_framework import serializers

from bot.models import TgUser


class VerificationSerializer(serializers.ModelSerializer):
    verification_code = serializers.CharField(write_only=True, max_length=5)

    class Meta:
        model = TgUser
        fields = ("tg_chat_id", "tg_user_id", "tg_username", "verification_code",)
        read_only_fields = ("tg_chat_id", "tg_user_id", "tg_username",)

    def validate(self, attrs: dict):
        """
        Проверяем правильность кода верификации.
        :param attrs:
        """
        verification_code = attrs.get("verification_code")
        tg_user = TgUser.objects.filter(verification_code__exact=verification_code).first()
        if not tg_user:
            raise ValidationError({"verification_code": "field is incorrect"})
        attrs["tg_user"] = tg_user
        return attrs
