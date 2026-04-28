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

# Работа с файлами
from os import remove as remove_file

# Формы
from .forms.question_create import QuestionCreateForm
from .forms.question_edit import QuestionEditForm
from .forms.question_search import QuestionSearchForm


@bp.route("/question/home", methods=["GET", "POST"])
@login_required
def question_home():
    """Меню с данными о вопросах пользователя"""

    return ""


@bp.route("/question/<int:question_id>/view", methods=["GET"])
def question_view(question_id: int):
    """Просмотр вопроса"""

    # Получение данных через REST API
    server_address = f"{request.scheme}://{request.host}"

    # Получение данных о вопросе через REST API
    # Запрос
    response = requests.get(f"{server_address}/api/v1/questions/{question_id}")

    # Обработка запроса
    question = response.json()["question"] if response else None

    # Получение данных об авторе вопроса
    if question and question["creator_id"]:
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

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

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
        json_params = {
            "name": question_create_form.name.data,
            "creator_id": current_user.id,
            "tags": question_create_form.tags.data.split(", "),
            "content": question_create_form.content.data,
            "is_solved": False,
            "is_closed": False
        }
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

    # Отображение страницы (GET)
    return render_template(
        "question_create.html",
        question_create_form=question_create_form
    )


@bp.route("/question/<int:question_id>/edit", methods=["GET", "POST"])
@login_required
def question_edit(question_id: int):
    """Редактирование вопроса"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Форма для изменения вопроса
    question_edit_form = QuestionEditForm()

    # Получение данных о вопросе через REST API
    # Запрос
    response: requests.Response = request_session.get(f"{server_address}/api/v1/questions/{question_id}")

    # Обработка запроса
    if response:
        # Получение данных о вопросе
        question = response.json()["question"]

        # Процесс редактирования вопроса (POST)
        if question_edit_form.validate_on_submit():
            # Обработка изображения
            image: FileStorage = question_edit_form.image.data
            if image:
                # Проверка на безопасность
                correct_extensions = question_edit_form.image.validators[0].upload_set
                is_safe, reason, secured_filename = Image.full_check(image.filename, correct_extensions, image.stream)

                if is_safe:
                    # Составление имени файла
                    file_extension = secured_filename.split(".")[-1]
                    filename = f"{current_user.id}_{current_user.login}_{question_edit_form.name.data}.{file_extension}"
                else:
                    flash(reason, "error")
                    return redirect(url_for("qa.question_edit", question_id=question_id))

            # Редактирование вопроса через REST API
            # Подготовка данных
            json_params = {
                "name": question_edit_form.name.data,
                "tags": question_edit_form.tags.data.split(", "),
                "content": question_edit_form.content.data
            }
            if image: json_params["image"] = filename
            # Запрос
            response: requests.Response = request_session.put(
                f"{server_address}/api/v1/questions/{question_id}",
                json=json_params,
                cookies=request.cookies
            )

            # Обработка запроса
            if response:
                if image:
                    # Удаление старого изображения
                    if question["image"]:
                        remove_file(f"{Config.static_url_path}/questions_images/{question["image"]}")
                    # Сохранение изображения
                    image.save(f"{Config.static_url_path}/questions_images/{filename}")

                # Перенос на страницу с отредактированным вопросом
                return redirect(url_for("qa.question_view", question_id=question_id))
            else:
                # Вывод ошибки, если что-то пошло не так
                try:
                    flash(response.json()["error"], "error")
                except:
                    flash("Something went wrong", "error")
                return redirect(url_for("qa.question_edit", question_id=question_id))
        else:
            # Подстановка текущих данных в поля
            question_edit_form.name.data = question["name"]
            question_edit_form.tags.data = ", ".join([tag["name"] for tag in question["tags"]])
            question_edit_form.content.data = question["content"]

        # Отображение страницы (GET)
        return render_template(
            "question_edit.html",
            question_edit_form=question_edit_form,
            question=question
        )

    # Вывод ошибки, если что-то пошло не так
    try:
        flash(response.json()["error"], "error")
    except:
        flash("Something went wrong", "error")
    # Возвращение в меню, если вопрос не удалось загрузить
    return redirect(url_for("qa.question_home"))


@bp.route("/question/<int:question_id>/delete", methods=["GET", "POST"])
@login_required
def question_delete(question_id: int):
    """Удаление вопроса"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Получение данных о вопросе через REST API
    # Запрос
    response: requests.Response = request_session.get(f"{server_address}/api/v1/questions/{question_id}")

    # Обработка запроса
    if response:
        # Получение данных о вопросе
        question = response.json()["question"]

        # Удаление вопроса через REST API
        # Запрос
        response: requests.Response = request_session.delete(
            f"{server_address}/api/v1/questions/{question_id}",
            cookies=request.cookies
        )

        # Обработка запроса
        if response:
            # Удаление изображения
            if question["image"]:
                remove_file(f"{Config.static_url_path}/questions_images/{question["image"]}")

            # Возвращение в меню
            return redirect(url_for("qa.question_home"))
        else:
            # Вывод ошибки, если что-то пошло не так
            try:
                flash(response.json()["error"], "error")
            except:
                flash("Something went wrong", "error")
    else:
        # Вывод ошибки, если что-то пошло не так
        try:
            flash(response.json()["error"], "error")
        except:
            flash("Something went wrong", "error")

    # Возвращение на предыдущую страницу
    next_url: str = request.args.get("next", url_for("qa.question_view", question_id=question_id))
    return redirect(next_url)


@bp.route("/question/<int:question_id>/delete/image", methods=["GET"])
@login_required
def question_delete_image(question_id: int):
    """Удаление изображения вопроса"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Получение данных о вопросе через REST API
    # Запрос
    response: requests.Response = request_session.get(f"{server_address}/api/v1/questions/{question_id}")

    # Обработка запроса
    if response:
        # Получение данных о вопросе
        question = response.json()["question"]

        if question["image"]:
            # Удаление названия изображения вопроса через REST API
            # Подготовка данных
            json_params = {
                "image": ""
            }
            # Запрос
            response: requests.Response = request_session.put(
                f"{server_address}/api/v1/questions/{question_id}",
                json=json_params,
                cookies=request.cookies
            )

            # Обработка запроса
            if response:
                # Удаление изображения
                remove_file(f"{Config.static_url_path}/questions_images/{question["image"]}")
            else:
                # Вывод ошибки, если что-то пошло не так
                try:
                    flash(response.json()["error"], "error")
                except:
                    flash("Something went wrong", "error")
    else:
        # Вывод ошибки, если что-то пошло не так
        try:
            flash(response.json()["error"], "error")
        except:
            flash("Something went wrong", "error")

    # Возвращение на предыдущую страницу
    next_url: str = request.args.get("next", url_for("qa.question_edit", question_id=question_id))
    return redirect(next_url)


@bp.route("/question/search", methods=["GET", "POST"])
def question_search():
    """Поиск вопросов"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"

    # Форма для поиска
    search_form = QuestionSearchForm()

    # Запрос на поиск через форму (POST)
    if search_form.validate_on_submit():
        # Обновление страницы с параметрами для поиска
        return redirect(url_for(
            "qa.question_search",
            search=search_form.search.data,
            search_mode="name"
        ))

    # Процесс поиска (параметры передаётся через параметры ссылки)
    if request.args.get("search_mode"):
        # Поиск вопросов через REST API
        # Подготовка данных
        json_params = {
            "search": request.args.get("search"),
            "search_mode": request.args.get("search_mode")
        }
        # Запрос
        response = requests.get(
            f"{server_address}/api/v1/questions",
            json=json_params
        )

        # Обработка запроса
        if response:
            # Получение данных
            found_questions = response.json()["questions"]

            # Отображение страницы (GET)
            return render_template(
                "question_search.html",
                search_form=search_form,
                found_questions=found_questions
            )
        else:
            # Вывод ошибки, если что-то пошло не так
            try:
                flash(response.json()["error"], "error")
            except:
                flash("Something went wrong", "error")
            return redirect(url_for("qa.question_search"))

    # Отображение страницы без данных для поиска (GET)
    return render_template(
        "question_search.html",
        search_form=search_form
    )
