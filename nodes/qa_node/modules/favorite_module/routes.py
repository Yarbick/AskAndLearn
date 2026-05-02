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


@bp.route("/<int:question_id>/create", methods=["GET"])
@login_required
def create(question_id: int):
    """Добавление вопроса в избранные"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Добавление вопроса в избранные через REST API
    # Подготовка данных
    json_params = {
        "question_id": question_id,
        "user_id": current_user.id
    }
    # Запрос
    response: requests.Response = request_session.post(
        f"{server_address}/api/v1/favorites",
        json=json_params,
        cookies=request.cookies
    )

    # Обработка запроса
    if response:
        # Вывод сообщения
        flash("Question added to favorites", "info")
    else:
        # Обработка ошибок
        ResponseErrorHandler.flash_reason_message(response)

    # Возвращение на предыдущую страницу
    next_url: str = request.args.get("next", url_for("question.view", question_id=question_id))
    return redirect(next_url)


@bp.route("/<int:favorite_id>/delete", methods=["GET"])
@login_required
def delete(favorite_id: int):
    """Удаление вопроса из избранных"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Удаление вопроса из избранных через REST API
    # Запрос
    response: requests.Response = request_session.delete(
        f"{server_address}/api/v1/favorites/{favorite_id}",
        cookies=request.cookies
    )

    # Обработка запроса
    if response:
        # Вывод сообщения
        flash("The question has been removed from favorites", "info")
    else:
        # Обработка ошибок
        ResponseErrorHandler.flash_reason_message(response)

    # Возвращение на предыдущую страницу
    next_url: str = request.args.get("next", url_for("question.home"))
    return redirect(next_url)
