"""Защита от CSRF атак"""

# Работа с фреймворком
from flask import url_for

# Работа с REST API
import requests


def create_csrf_request_session(server_address: str) -> tuple[requests.Session]:
    """Создание сессии с CSRF-токеном"""

    # Создание сессии
    request_session = requests.Session()

    # Получение CSRF-токена
    response = request_session.get(f"{server_address}{url_for("get_csrf_token")}")
    csrf_token: str = response.json()["csrf_token"]
    # Добавление токена в заголовок
    request_session.headers["X-CSRFToken"] = csrf_token

    return request_session
