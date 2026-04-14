"""Auth Blueprint"""

# Работа с фреймворком
from flask import Blueprint
from jinja2 import FileSystemLoader

# Работа с файлами
from os.path import join as path_join

# Настройки модуля
from . import config

# Создание и настройка модуля
bp = Blueprint(
    config["name"],
    __name__,
    url_prefix=config["url_prefix"],
    template_folder=path_join(config["path"], config["self_templates_folder"])
)
bp.jinja_loader = FileSystemLoader(
    [bp.template_folder] +
    [path_join(config["path"], template_folder) for template_folder in config["other_templates_folders"]]
)
