from django.conf import settings
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bot.models import TgUser
from bot.serializers import VerificationSerializer
from bot.tg.client import TgClient


class VerificationView(GenericAPIView):
    model = TgUser
    serializer_class = VerificationSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        serializer: VerificationSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tg_user: TgUser = serializer.validated_data["tg_user"]
        tg_user.user = self.request.user # связываем юзеров
        tg_user.verification_code = None # Для того чтобы успешно использованный код
        # нельзя было использовать повторно
        tg_user.save(update_fields=["user", "verification_code"])
        instance_serializer: VerificationSerializer = self.get_serializer(tg_user)
        tg_client = TgClient(settings.BOT_TOKEN)
        tg_client.send_message(tg_user.tg_chat_id, "[Верификация пройдена успешно]")

        return Response(instance_serializer.data)
