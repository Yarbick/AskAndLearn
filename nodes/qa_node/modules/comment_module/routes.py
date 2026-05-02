"""Обработчики маршрутов модуля Comment"""

# Работа с фреймворком
from flask import render_template, url_for, redirect, request, flash
from flask_login import login_required

# Безопасность
from security.csrf import create_csrf_request_session

# Обработка ошибок
from exceptions.api.rest.shared import ResponseErrorHandler

# Подключение к модулю
from .blueprint import bp

# Работа с REST API
import requests

# Формы
from .forms.comment.edit import CommentEditForm


@bp.route("/<int:comment_id>/edit", methods=["GET", "POST"])
@login_required
def edit(comment_id: int):
    """Редактирование комментария"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Форма для редактирования комментария
    comment_edit_form = CommentEditForm()

    # Получение данных о комментарии через REST API
    # Запрос
    response: requests.Response = request_session.get(f"{server_address}/api/v1/comments/{comment_id}")

    # Обработка запроса
    if response:
        comment = response.json()["comment"]

        # Редактирование комментария (POST)
        if comment_edit_form.validate_on_submit():
            # Редактирование комментария через REST API
            # Подготовка данных
            json_params = {
                "content": comment_edit_form.content.data
            }
            # Запрос
            response: requests.Response = request_session.put(
                f"{server_address}/api/v1/comments/{comment_id}",
                json=json_params,
                cookies=request.cookies
            )

            # Обработка запроса
            if response:
                # Вывод сообщения
                flash("The comment has been edited", "info")

                # Возвращение на страницу с вопросом
                return redirect(url_for("question.view", question_id=comment["question_id"]))
            else:
                # Обработка ошибок
                ResponseErrorHandler.flash_reason_message(response)
        else:
            # Устанавливаем текущие значения комментария в форму
            comment_edit_form.content.data = comment["content"]
    else:
        # Обработка ошибок
        ResponseErrorHandler.flash_reason_message(response)

    # Отображение страницы (GET)
    return render_template(
        "comment/edit.html",
        comment_edit_form=comment_edit_form
    )


@bp.route("/<int:comment_id>/delete", methods=["GET"])
@login_required
def delete(comment_id: id):
    """Удаление комментария"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Удаление комментария через REST API
    # Запрос
    response: requests.Response = request_session.delete(
        f"{server_address}/api/v1/comments/{comment_id}",
        cookies=request.cookies
    )

    # Обработка запроса
    if response:
        # Вывод сообщения
        flash("Comment deleted", "info")
    else:
        # Обработка ошибок
        ResponseErrorHandler.flash_reason_message(response)

    # Возвращение на предыдущую страницу
    next_url: str = request.args.get("next", url_for("question.home"))
    return redirect(next_url)


@bp.route("/<int:comment_id>/useful/<string:useful_status>", methods=["GET"])
@login_required
def set_useful(comment_id: int, useful_status: str):
    """Изменение состояния is_useful"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Изменение состояния is_closed через REST API
    # Подготовка данных
    json_params = {
        "is_useful": useful_status == "true"
    }
    # Запрос
    response: requests.Response = request_session.patch(
        f"{server_address}/api/v1/comments/{comment_id}",
        json=json_params,
        cookies=request.cookies
    )

    # Обработка запроса
    if not response:
        # Обработка ошибок
        ResponseErrorHandler.flash_reason_message(response)

    # Возвращение на предыдущую страницу
    next_url: str = request.args.get("next", url_for("question.home"))
    return redirect(next_url)
