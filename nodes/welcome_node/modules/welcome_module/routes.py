"""Обработчики маршрутов модуля Welcome"""

# Работа с фреймворком
from flask import render_template

# Подключение к модулю
from .blueprint import bp


@bp.route("/", methods=["GET"])
def root():
    """Главная страница"""

    return render_template(
        "welcome.html"
    )
