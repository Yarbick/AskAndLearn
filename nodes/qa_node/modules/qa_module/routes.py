"""Обработчики маршрутов модуля QA"""

# Работа с фреймворком
from flask import render_template, url_for, redirect, request, flash
from flask_login import current_user, login_required

# Безопасность
from security.csrf import create_csrf_request_session
from security.file import Image

# Подключение к модулю
from .blueprint import bp

# Настройки модуля
from .config import Config

# Работа с REST API
import requests

# Формы
from .forms.question_create import QuestionCreateForm


@bp.route("/question/<int:question_id>/view", methods=["GET"])
def question_view(question_id: int):
    """Просмотр вопроса"""

    # Получение данных через REST API
    server_address = f"{request.scheme}://{request.host}"

    # Получение данных о вопросе
    response = requests.get(f"{server_address}/api/v1/questions/{question_id}")
    question = response.json()["question"] if response else None

    # Получение данных об авторе вопроса
    if question["creator_id"]:
        response = requests.get(f"{server_address}/api/v1/users/{question["creator_id"]}")
        question_creator = response.json()["user"] if response else None
    else:
        question_creator = None

    # Отображение страницы (GET)
    return render_template(
        "question_view.html",
        question=question,
        question_creator=question_creator
    )


@bp.route("/question/create", methods=["GET", "POST"])
@login_required
def question_create():
    """Создание вопроса"""

    # Форма для создания вопроса
    question_create_form = QuestionCreateForm()

    # Процесс создания формы (POST)
    if question_create_form.validate_on_submit():
        # Обработка изображения
        image: FileStorage = question_create_form.image.data
        if image:
            # Проверка на безопасность
            correct_extensions = question_create_form.image.validators[0].upload_set
            is_safe, reason, secured_filename = Image.full_check(image.filename, correct_extensions, image.stream)

            if is_safe:
                # Составление имени файла
                file_extension = secured_filename.split(".")[-1]
                filename = f"{current_user.id}_{current_user.login}_{question_create_form.name.data}.{file_extension}"
            else:
                flash(reason, "error")
                return redirect(url_for("qa.question_create"))

        # Создание вопроса через REST API
        # Подготовка данных
        server_address = f"{request.scheme}://{request.host}"
        request_session: requests.Session = create_csrf_request_session(server_address)
        json_params = {
            "name": question_create_form.name.data,
            "creator_id": current_user.id,
            "is_solved": False,
            "is_closed": False
        }
        if question_create_form.tags.data: json_params["tags"] = question_create_form.tags.data.split(", ")
        if question_create_form.content.data: json_params["content"] = question_create_form.content.data
        if image: json_params["image"] = filename
        # Запрос
        response: requests.Response = request_session.post(
            f"{server_address}/api/v1/questions",
            json=json_params,
            cookies=request.cookies
        )

        # Обработка запроса
        if response:
            # Сохранение изображения
            if image: image.save(f"{Config.static_url_path}/questions_images/{filename}")

            # Получение ID нового вопроса
            question_id: int = response.json()["id"]

            # Перенос на страницу с созданным вопросом
            return redirect(url_for("qa.question_view", question_id=question_id))
        else:
            # Вывод ошибки, если что-то пошло не так
            try:
                flash(response.json()["error"], "error")
            except:
                flash("Something went wrong", "error")
            return redirect(url_for("qa.question_create"))

    # Проверка на правильное расширение файла (если обнаружила форма)
    if question_create_form.image.errors:
        for error in question_create_form.image.errors:
            flash(error, "error")
        return redirect(url_for("qa.question_create"))

    # Отображение страницы (GET)
    return render_template(
        "question_create.html",
        question_create_form=question_create_form
    )
