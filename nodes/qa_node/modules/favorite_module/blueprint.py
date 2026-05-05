"""Создание Blueprint модуля"""

# Работа с фреймворком
from flask import Blueprint
from jinja2 import FileSystemLoader

# Настройки модуля
from .config import Config

# Создание и настройка Blueprint
bp: Blueprint = Blueprint(
    Config.NAME,
    __name__,
    url_prefix=Config.URL_PREFIX,
    static_folder=Config.STATIC_FOLDER,
    static_url_path=Config.STATIC_URL_PATH,
    template_folder=Config.SELF_TEMPLATE_FOLDER
)
bp.jinja_loader = FileSystemLoader([bp.template_folder] + list(Config.OTHER_TEMPLATE_FOLDERS))
