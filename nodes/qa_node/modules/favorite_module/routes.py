"""Обработчики маршрутов модуля Favorite"""

# Работа с фреймворком
from flask import render_template, url_for, redirect, request, flash, session as flask_session
from flask_login import current_user, login_required

# Безопасность
from security.csrf import create_csrf_request_session

# Обработка ошибок
from exceptions.api.rest.shared import ResponseErrorHandler

# Подключение к модулю
from .blueprint import bp

# Работа с REST API
import requests


@bp.route("/view", methods=["GET"])
@login_required
def view():
    """Просмотр избранных вопросов у пользователя"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"

    # Получение избранных вопросов пользователя через REST API
    # Подготовка данных
    json_params = {
        "search": current_user.id,
        "search_mode": "user"
    }
    # Запрос
    response: requests.Response = requests.get(
        f"{server_address}/api/v1/favorites",
        json=json_params
    )

    # Обработка запроса
    if response:
        favorites = response.json()["favorites"]

        # Отображение страницы (GET)
        return render_template(
            "favorite/view.html",
            favorites=favorites
        )

    # Отображение страницы в случае ошибки (GET)
    return render_template(
        "favorite/view.html",
        error_message=response.reason
    )


@bp.route("/<int:favorite_id>/delete", methods=["GET"])
@login_required
def delete(favorite_id: int):
    """Удаление вопроса из избранных"""

    pass
