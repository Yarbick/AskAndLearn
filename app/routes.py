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


@app.route("/")
def root():
    """Временный обработчик для главной страницы"""

    from flask import render_template
    from flask_login import current_user

    return render_template(
        "base.html",
        current_user=current_user
    )
