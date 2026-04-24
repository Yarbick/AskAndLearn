"""Обработчики маршрутов главного приложения"""

# Работа с фреймворком
from flask import jsonify

# Работа с формами
from flask_wtf.csrf import generate_csrf

# Подключение к приложению
from .app import app


@app.route("/get_csrf_token", methods=["GET"])
def get_csrf_token():
    """Получение CSRF-токена"""

    return jsonify({"csrf_token": generate_csrf()})
