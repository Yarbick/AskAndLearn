"""Методы защиты пользователя"""

# Работа с фреймворком
from flask import url_for, session as flask_session

# Безопасность
from security.csrf import create_csrf_request_session

# Работа с REST API
import requests


def create_user_request_session(server_address: str) -> requests.Session:
    """Создание сессии с Auth и CSRF токеном"""

    # Создание сессии с CSRF-токеном
    request_session: requests.Session = create_csrf_request_session(server_address)
    # Добавление токена аутентификации в заголовок из Cookie
    request_session.headers["Auth-Token"] = flask_session.get("auth_token")

    return request_session
