"""Обработка общих ошибок для всех REST API"""

# Работа с фреймворком
from flask import flash

# Работа с REST API
import requests


class ResponseErrorHandler:
    """Класс для обработки ошибок в ответах на запрос"""

    @staticmethod
    def flash_reason_message(wrong_response: requests.Response) -> None:
        """Возвращение ошибки через flash в cookie"""

        try:
            # Вывод переданных в ответе ошибок
            errors: dict = wrong_response.json()
            for message in errors.values(): flash(message, "error")
        except:
            # Вывод сообщения из reason в противном случае
            flash(wrong_response.reason, "error")
