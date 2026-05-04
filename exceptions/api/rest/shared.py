"""Обработка общих ошибок для всех REST API"""

# Работа с фреймворком
from flask import flash

# Работа с REST API
import requests


class ResponseErrorHandler:
    """Класс для обработки ошибок в ответе запроса"""

    @staticmethod
    def flash_reason_message(wrong_response: requests.Response) -> None:
        """Вывод ошибок через flash в cookie"""

        try:
            # Вывод переданных в ответе ошибок
            errors: dict = wrong_response.json()
            for error in errors.values():
                flash(error, "error")
        except:
            # Вывод сообщения из reason в противном случае
            flash(wrong_response.reason, "error")
