"""Настройки модуля"""

# Работа с путями
from os.path import join as join_path, dirname

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class Config:
    """Настройки модуля"""

    # Параметры
    PATH: str = dirname(__file__)
    NAME: str = "welcome"
    URL_PREFIX: str = ""
    STATIC_FOLDER: str = "static"
    STATIC_URL_PATH: str = join_path(PATH, STATIC_FOLDER)
    SELF_TEMPLATE_FOLDER: str = join_path(PATH, "templates")
    OTHER_TEMPLATE_FOLDERS: tuple[str] = ("shared_templates",)
