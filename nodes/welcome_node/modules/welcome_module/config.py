"""Настройки модуля"""

# Работа с путями
from os.path import join as join_path, dirname

# Работа с классами для хранения
from dataclasses import dataclass


@dataclass
class Config:
    """Настройки модуля"""

    # Параметры
    path = dirname(__file__)
    name = "welcome"
    url_prefix = ""
    static_folder = "static"
    static_url_path = join_path(path, static_folder)
    self_template_folder = join_path(path, "templates")
    other_template_folders = ["shared_templates"]
