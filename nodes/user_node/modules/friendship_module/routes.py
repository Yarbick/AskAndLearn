"""Обработчики маршрутов модуля Friendship"""

# Работа с фреймворком
from flask import render_template, url_for, redirect, request, flash
from flask_login import current_user, login_required

# Безопасность
from security.csrf import create_csrf_request_session

# Подключение к модулю
from .blueprint import bp

# Работа с REST API
import requests


def create_friendship_view_handler(friendship_status: str) -> str:
    """Создание обработчика для просмотра связей пользователя с другими пользователями по статусу отношений"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"

    # Дополнительные данные для отображения страницы
    title: str = friendship_status.lower().capitalize()

    # Получение связей с пользователями через REST API
    # Подготовка данных
    json_params = {
        "search": friendship_status.lower(),
        "search_mode": "status"
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


@bp.route("/accept/<int:friend_id>", methods=["GET"])
@login_required
def accept(friend_id: int):
    """Удаление связи между пользователями"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Удаление связи между пользователями через REST API
    # Подготовка данных
    json_params = {
        "status": "accepted"
    }
    # Запрос
    response: requests.Response = request_session.put(
        f"{server_address}/api/v1/users/{current_user.id}/friendships/{friend_id}",
        json=json_params,
        cookies=request.cookies
    )

    # Обработка запроса
    if not response:
        # Обработка ошибок
        try:
            flash(response.json()["error"], "error")
        except:
            flash("Something went wrong", "error")
    else:
        flash("Friend request accepted", "info")

    # Возвращение на предыдущую страницу
    next_url: str = request.args.get("next", url_for("friendship.view_pending", friend_id=friend_id))
    return redirect(next_url)


@bp.route("/send_request/<int:friend_id>", methods=["GET"])
@login_required
def send_request(friend_id: int):
    """Создание запроса на дружбу с пользователем"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Создание связей между пользователями через REST API
    # Подготовка данных
    json_params = {
        "friend_id": friend_id,
        "status": "pending"
    }
    # Запрос
    response = request_session.post(
        f"{server_address}/api/v1/users/{current_user.id}/friendships",
        json=json_params
    )

    # Обработка запроса
    if not response:
        # Обработка ошибок
        try:
            flash(response.json()["error"], "error")
        except:
            flash("Something went wrong", "error")
    else:
        flash("The request has been sent", "info")

    # Возвращение на предыдущую страницу
    next_url: str = request.args.get("next", url_for("user.view", user_id=friend_id))
    return redirect(next_url)


@bp.route("/block/<int:friend_id>", methods=["GET"])
@login_required
def block(friend_id: int):
    """Блокировка пользователя"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Блокировка пользователя через REST API
    json_params = {
        "friend_id": friend_id,
        "status": "blocked"
    }
    # Запрос
    response: requests.Response = request_session.put(
        f"{server_address}/api/v1/users/{current_user.id}/friendships/{friend_id}",
        json={"status": json_params["status"]},
        cookies=request.cookies
    )

    # Обработка запроса
    if not response:
        if response.status_code == 404:
            # Создание новых отношений с блокировкой
            # Запрос
            response: requests.Response = request_session.post(
                f"{server_address}/api/v1/users/{current_user.id}/friendships",
                json=json_params
            )

            # Обработка ошибок
            if not response:
                try:
                    flash(response.json()["error"], "error")
                except:
                    flash("Something went wrong", "error")
            else:
                flash("The user is blocked", "info")
        else:
            # Обработка ошибок
            try:
                flash(response.json()["error"], "error")
            except:
                flash("Something went wrong", "error")
    else:
        flash("The user is blocked", "info")

    # Возвращение на предыдущую страницу
    next_url: str = request.args.get("next", url_for("user.view", user_id=friend_id))
    return redirect(next_url)


@bp.route("/delete/<int:friend_id>", methods=["GET"])
@login_required
def delete(friend_id: int):
    """Удаление связи между пользователями"""

    # Подготовка данных через REST API
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Удаление связи между пользователями через REST API
    # Запрос
    response: requests.Response = request_session.delete(
        f"{server_address}/api/v1/users/{current_user.id}/friendships/{friend_id}",
        cookies=request.cookies
    )

    # Обработка запроса
    if not response:
        # Обработка ошибок
        try:
            flash(response.json()["error"], "error")
        except:
            flash("Something went wrong", "error")
    else:
        flash("The friendship was successfully deleted", "info")

    # Возвращение на предыдущую страницу
    next_url: str = request.args.get("next", url_for("friendship.view_accepted", friend_id=friend_id))
    return redirect(next_url)
