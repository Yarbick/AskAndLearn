"""Инициализация модуля Auth"""

# Работа с фреймворком
from flask import json

# Работа с файлами
from os.path import dirname

# Чтение настроек модуля из файлов
with open(f"{dirname(__file__)}/config.json", mode="rb") as file:
    config = json.load(file)
    config["path"] = dirname(__file__)

# Создание blueprint
from .blueprint import bp
