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
    name = "auth"
    url_prefix = "/auth"
    static_folder = join_path(path, "static")
    self_template_folder = join_path(path, "templates")
    other_template_folders = ["shared_templates"]
