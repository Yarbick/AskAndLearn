"""Обработчики маршрутов главного приложения"""

# Работа с фреймворком
from flask import redirect, url_for

# Подключение к приложению
from .app import app


@app.errorhandler(401)
def unauthorized(error):
    """Предложение зарегистрироваться при ошибке 401"""

    return redirect(url_for("auth.register"))
