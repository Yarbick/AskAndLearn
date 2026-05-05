"""Обработчики маршрутов модуля"""

# Работа с фреймворком
from flask import render_template

# Подключение к модулю
from .blueprint import bp


@bp.route("/", methods=["GET"])
def root():
    """Главная страница"""

    # Отображение страницы (GET)
    return render_template(
        "welcome/welcome.html"
    )
