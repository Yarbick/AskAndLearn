"""Обработчики маршрутов модуля Friendship"""

# Работа с фреймворком
from flask import render_template, url_for, redirect, request, flash
from flask_login import current_user, login_required

# Подключение к модулю
from .blueprint import bp

# Работа с REST API
import requests


def create_friendship_view_handler(friendship_status: str) -> str:
    """Создание обработчика для просмотра связей пользователя с другими пользователями по статусу отношений"""

    # Дополнительные данные для отображения страницы
    title: str = friendship_status.lower().capitalize()

    # Получение связей с пользователями через REST API
    # Подготовка данных
    server_address = f"{"https" if request.is_secure else "http"}://{request.host}"
    json_params = {
        "status": friendship_status.lower()
    }
    # Запрос
    response = requests.get(
        f"{server_address}/api/v1/users/{current_user.id}/friendships",
        json=json_params
    )

    # Обработка запроса
    if response:
        # Получение связей с другими пользователями
        user_friendships: dict = response.json()["friendships"]

        # Отображение страницы (GET)
        return render_template(
            "friendships.html",
            title=title,
            user_friendships=user_friendships
        )
    # Отображение страницы в случае ошибки (GET)
    return render_template(
        "friendships.html",
        title=title,
        error_message=response.reason
    )


@bp.route("/view/accepted", methods=["GET"])
@login_required
def view_accepted():
    """Просмотр друзей пользователя"""

    return create_friendship_view_handler("accepted")


@bp.route("/view/pending", methods=["GET"])
@login_required
def view_pending():
    """Просмотр аккаунтов с приглашением в друзья от пользователя"""

    return create_friendship_view_handler("pending")


@bp.route("/view/blocked", methods=["GET"])
@login_required
def view_blocked():
    """Просмотр заблокированных аккаунтов пользователем"""

    return create_friendship_view_handler("blocked")
