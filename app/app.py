"""Приложение"""

# Работа с фреймворком
from flask import Flask, json

# Работа с файлами
from os import getenv
from dotenv import load_dotenv
from os.path import dirname

# Работа с временем
from datetime import timedelta

# Чтение настроек приложения из файлов
load_dotenv(".env")
with open(f"{dirname(__file__)}/config.json", mode="rb") as file:
    config = json.load(file)
    config["path"] = dirname(__file__)

# Создание и настройка приложения
app = Flask(
    "AskAndLearn",
    static_folder=config["static_folder"],
    template_folder=config["template_folder"]
)
app.config["SECRET_KEY"] = getenv("SECRET_KEY")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=config["permanent_session_lifetime_days"])
