"""Приложение"""

# Работа с фреймворком
from flask import Flask, json

# Работа с файлами
from os import getenv

# Работа с временем
from datetime import timedelta

# Настройки приложения
from . import config

# Модули приложения
from modules.user_node.auth import bp as auth_bp

# Создание и настройка приложения
app = Flask(
    "AskAndLearn",
    static_folder=config["static_folder"],
    template_folder=config["template_folder"]
)
app.config["SECRET_KEY"] = getenv("SECRET_KEY")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=config["permanent_session_lifetime_days"])
# Подключение модулей
app.register_blueprint(auth_bp)
