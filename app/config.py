"""Настройки приложения"""

# Работа с фреймворком
from flask import request

# Безопасность
from os import urandom

# Работа с путями
from os.path import join as join_path, dirname

# Работа с виртуальным окружением
from os import getenv

# Работа с временем
from datetime import timedelta

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class Config:
    """Настройки приложения"""

    # Параметры
    PATH: str = dirname(__file__)
    NAME: str = "AskAndLearn"
    SECRET_KEY: str = urandom(32)
    STATIC_FOLDER: str = "shared/static"
    STATIC_URL_PATH: str = "/shared/static"
    TEMPLATE_FOLDER: str = "shared/templates"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024
    WTF_CSRF_ENABLED: bool = True
    WTF_CSRF_CHECK_DEFAULT: bool = True
    WTF_CSRF_HEADERS: tuple[str] = ("X-CSRFToken",)
    SESSION_COOKIE_NAME: str = "askandlearn_session"
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    SESSION_REFRESH_EACH_REQUEST: bool = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    FORCE_HTTPS: bool = False
    DEBUG: bool = False
    TESTING: bool = False


def get_server_address() -> str:
    """Получение адреса сервера"""

    # Получение адреса
    scheme: str = request.scheme
    host: str = request.host
    server_address: str = f"{scheme}://{host}"

    return server_address
