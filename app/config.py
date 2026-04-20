"""Настройки приложения"""

# Работа с переменными окружения
from os import getenv
from dotenv import load_dotenv

# Работа с путями
from os.path import join as join_path, dirname

# Работа с временем
from datetime import timedelta

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class Config:
    """Настройки приложения"""

    # Загрузка окружения
    load_dotenv(".env")

    # Параметры
    path = dirname(__file__)
    secret_key = getenv("SECRET_KEY")
    static_folder = "shared_static"
    static_url_path = "/"
    template_folder = join_path(path, "shared_templates")
    max_content_length = 16 * 1024 * 1024
    wtf_csrf_enabled = True
    wtf_csrf_check_default = True
    wtf_csrf_headers = ['X-CSRFToken']
    permanent_session_lifetime = timedelta(days=7)
