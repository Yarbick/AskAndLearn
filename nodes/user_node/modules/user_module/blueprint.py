"""User Blueprint"""

# Работа с фреймворком
from flask import Blueprint
from jinja2 import FileSystemLoader

# Настройки модуля
from .config import Config

# Создание и настройка Blueprint
bp = Blueprint(
    Config.name,
    __name__,
    url_prefix=Config.url_prefix,
    static_folder=Config.static_folder,
    static_url_path=Config.static_url_path,
    template_folder=Config.self_template_folder
)
bp.jinja_loader = FileSystemLoader([bp.template_folder] + Config.other_template_folders)
