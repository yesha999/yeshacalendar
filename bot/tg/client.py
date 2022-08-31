import requests

from bot.tg.dc import GetUpdatesResponse, SendMessageResponse


class TgClient:
    def __init__(self, token):
        self.token = token

    def _get_url(self, method: str):
        """
        Функция для внутреннего использования в классе, возвращает ссылку, с необходимым токеном бота и методом
        :param method:
        :return: ссылка
        """
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        """
        Создается урл для оповещений, получает новые сообщения в ТГ
        :param offset:
        :param timeout:
        """
        url = self._get_url("getUpdates")
        resp = requests.get(url, params={"offset": offset, "timeout": timeout})
        return GetUpdatesResponse.Schema().load(resp.json())

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        """
        создается урл для отправки сообщения юзерам в ТГ, отправляет сообщения
        :param chat_id:
        :param text:
        """
        url = self._get_url("sendMessage")
        resp = requests.get(url, params={"chat_id": chat_id, "text": text})
        return SendMessageResponse.Schema().load(resp.json())
