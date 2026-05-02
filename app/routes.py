"""Обработчики маршрутов главного приложения"""

# Работа с фреймворком
from flask import jsonify, redirect, url_for

# Работа с формами
from flask_wtf.csrf import generate_csrf

# Подключение к приложению
from .app import app


@app.errorhandler(401)
def unauthorized(error):
    """Предложение зарегистрироваться при ошибке 401"""

    return redirect(url_for("auth.register"))


@app.route("/get_csrf_token", methods=["GET"])
def get_csrf_token():
    """Получение CSRF-токена"""

    return jsonify({"csrf_token": generate_csrf()})
