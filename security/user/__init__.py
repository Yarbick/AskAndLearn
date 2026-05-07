"""Методы и функции для защиты пользователя"""

# Работа с фреймворком
from flask import session as flask_session

# Работа с REST API
import requests


def create_user_request_session() -> requests.Session:
    """Создание сессии с Auth и CSRF токеном"""

    # Создание сессии
    request_session: requests.Session = requests.Session()

    # Добавление токена аутентификации в заголовок из Cookie
    request_session.headers["Auth-Token"] = flask_session.get("auth_token")

    return request_session
