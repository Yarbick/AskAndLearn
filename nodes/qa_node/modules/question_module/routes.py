"""Обработчики маршрутов модуля"""

# Работа с фреймворком
from flask import render_template, url_for, redirect, request, flash, session as flask_session

# Работа с пользователем
from flask_login import current_user, login_required

# Безопасность
from security.csrf import create_csrf_request_session
from security.file import Image
from security.xss import clean_html

# Обработка ошибок
from exceptions.api.rest.shared import ResponseErrorHandler

# Подключение к модулю
from .blueprint import bp

# Настройки приложения
from app.config import get_server_address
from .config import Config

# Работа с REST API
import requests

# Работа с файлами
from werkzeug.datastructures import FileStorage
from os import remove as remove_file

# Формы для вопросов
from .forms.question.create import QuestionCreateForm
from .forms.question.edit import QuestionEditForm
from .forms.question.search import QuestionSearchForm
# Формы для комментариев
from .forms.comment.create import CommentCreateForm


@bp.route("", methods=["GET"])
@login_required
def home():
    """Главное меню модуля"""

    # Подготовка данных для REST API
    server_address: str = get_server_address()

    # Получение новейших вопросов через REST API
    # Подготовка данных
    json_params: dict = {
        "limit": 5
    }
    # Запрос
    response: requests.Response = requests.get(
        f"{server_address}/api/v1/questions",
        json=json_params
    )

    # Обработка запроса
    # Получение новейших вопросов
    newest_questions: list[dict] = response.json()["questions"] if response else []

    # Получение последних посещённых запросов из cookie-сессий
    last_questions: list[dict] = []
    last_questions_ids: list[int] = flask_session.get("last_questions", [])
    for question_id in last_questions_ids:
        # Получение вопроса через REST API
        # Запрос
        response: requests.Response = requests.get(
            f"{server_address}/api/v1/questions/{question_id}"
        )

        # Обработка запроса
        if response:
            # Добавление вопроса в список
            question = response.json()["question"]
            last_questions.append(question)

    # Получение вопросов, созданных пользователем, через REST API
    # Подготовка данных
    json_params: dict = {
        "filter": int(current_user.id),
        "filter_mode": "creator"
    }
    # Запрос
    response: requests.Response = requests.get(
        f"{server_address}/api/v1/questions",
        json=json_params
    )

    # Обработка запроса
    # Получение вопросов, созданных пользователем
    your_questions: list = response.json()["questions"] if response else []

    # Отображение страницы (GET)
    return render_template(
        "question/home.html",
        newest_questions=newest_questions,
        last_questions=last_questions,
        your_questions=your_questions
    )


@bp.route("/<int:question_id>/view", methods=["GET", "POST"])
def view(question_id: int):
    """Просмотр вопроса и создание комментариев"""

    # Подготовка данных для REST API
    server_address: str = get_server_address()
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Форма для создания комментария
    comment_create_form: CommentCreateForm = CommentCreateForm()

    # Создание комментария (POST)
    if comment_create_form.validate_on_submit():
        # Чтение данных из формы
        content: str = clean_html(comment_create_form.content.data)

        # Создание комментария через REST API
        # Подготовка данных
        json_params: dict = {
            "content": content,
            "creator_id": current_user.id,
            "question_id": question_id
        }
        # Запрос
        response: requests.Response = request_session.post(
            f"{server_address}/api/v1/comments",
            json=json_params,
            cookies=request.cookies
        )

        # Обработка запроса
        if response:
            # Вывод сообщения
            flash("The comment has been created", "info")
        else:
            # Обработка ошибок
            ResponseErrorHandler.flash_reason_message(response)

        # Обновление страницы
        return redirect(url_for("question.view", question_id=question_id))

    # Получение данных о вопросе через REST API
    # Запрос
    response: requests.Response = request_session.get(f"{server_address}/api/v1/questions/{question_id}")

    # Обработка запроса
    question: dict | None = None
    if response:
        question = response.json()["question"]

        # Запись посещения вопроса в сессию
        if current_user.is_authenticated:
            # Получение cookie-сессии последних вопросов
            if not flask_session.get("last_questions", None):  # Создаём список, если сессии не существует
                flask_session["last_questions"] = []
            last_question: list[int] = flask_session["last_questions"]

            # Добавление вопроса в список
            if question_id not in last_question:  # Если не существует, то просто добавляем
                flask_session["last_questions"] = ([question_id] + last_question)[:5]
            else:  # Если существует, то удаляем старое посещение и добавляем новое
                ind = last_question.index(question_id)
                flask_session["last_questions"] = ([question_id] + last_question[:ind] + last_question[ind + 1:])[:5]
            flask_session.permanent = True

    # Получение данных об авторе вопроса
    question_creator: dict | None = None
    if question and question["creator_id"]:
        # Получение данных об авторе вопроса через REST API
        # Запрос
        response: requests.Response = request_session.get(
            f"{server_address}/api/v1/users/{question["creator_id"]}"
        )

        # Обработка данных
        # Получение автора
        question_creator = response.json()["user"] if response else None

    # Получение данных о комментариях на вопрос
    comments: list[dict] = []
    if question:
        # Получение комментариев через REST API
        # Подготовка данных
        json_params: dict = {
            "sort_mode": "new",
            "filter": str(question_id),
            "filter_mode": "question"
        }
        # Запрос
        response: requests.Response = request_session.get(
            f"{server_address}/api/v1/comments",
            json=json_params
        )

        # Обработка запроса
        if response:
            # Получение комментариев
            comments = response.json()["comments"]

            # Получение информации об авторах комментариев
            creators_cash: dict = {}  # Сохраняем пользователей, чтобы не повторять запросы
            for comment in comments:
                if not comment["creator_id"] and comment["creator_id"] != 0:
                    comment["creator"] = None
                elif creators_cash.get(comment["creator_id"]):
                    comment["creator"] = creators_cash.get(comment["creator_id"])
                else:
                    # Получение пользователя через REST API
                    # Запрос
                    response: requests.Response = request_session.get(
                        f"{server_address}/api/v1/users/{comment["creator_id"]}"
                    )

                    # Обработка запроса
                    # Получение данных о пользователе
                    creator = response.json()["user"] if response else None
                    # Добавление пользователя в кеш и список
                    creators_cash[comment["creator_id"]] = creator
                    comment["creator"] = creator

    # Получение данных об избранных
    favorites: list[dict] = []
    if question:
        # Получение данных об избранных через REST API
        # Подготовка данных
        json_params: dict = {
            "filter": question["id"],
            "filter_mode": "question"
        }
        # Запрос
        response: requests.Response = request_session.get(
            f"{server_address}/api/v1/favorites",
            json=json_params
        )

        # Обработка запроса
        if response:
            favorites = response.json()["favorites"]

    # Отображение страницы (GET)
    return render_template(
        "question/view.html",
        comment_create_form=comment_create_form,
        question=question,
        question_creator=question_creator,
        comments=comments,
        favorites=favorites
    )


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Создание вопроса"""

    # Подготовка данных для REST API
    server_address: str = get_server_address()
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Форма для создания вопроса
    question_create_form: QuestionCreateForm = QuestionCreateForm()

    # Процесс создания формы (POST)
    if question_create_form.validate_on_submit():
        # Чтение данных из формы
        name: str = clean_html(question_create_form.name.data)
        tags: str = clean_html(question_create_form.tags.data)
        content: str = clean_html(question_create_form.content.data)

        # Обработка изображения
        image: FileStorage = question_create_form.image.data
        if image:
            # Проверка на безопасность
            correct_extensions: list[str] = question_create_form.image.validators[0].upload_set
            is_safe, reason, secured_filename = Image.full_check(image.filename, correct_extensions, image.stream)

            if is_safe:
                # Составление имени файла
                file_extension: str = secured_filename.split(".")[-1]
                filename: str = Image.full_clearing_filename(
                    f"{current_user.id}_{current_user.login}_{name}.{file_extension}"
                )
            else:
                # Обработка ошибок
                flash(reason, "error")
                return redirect(url_for("question.create"))

        # Создание вопроса через REST API
        # Подготовка данных
        json_params: dict = {
            "name": name,
            "creator_id": current_user.id,
            "tags": tags,
            "content": content
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
            if image: image.save(f"{Config.STATIC_URL_PATH}/questions_images/{filename}")

            # Вывод сообщения
            flash("The question has been created", "info")

            # Получение ID нового вопроса
            question_id: int = response.json()["id"]

            # Перенос на страницу с созданным вопросом
            return redirect(url_for("question.view", question_id=question_id))
        else:
            # Обработка ошибок
            ResponseErrorHandler.flash_reason_message(response)

    # Отображение страницы (GET)
    return render_template(
        "question/create.html",
        question_create_form=question_create_form
    )


@bp.route("/<int:question_id>/edit", methods=["GET", "POST"])
@login_required
def edit(question_id: int):
    """Редактирование вопроса"""

    # Подготовка данных для REST API
    server_address: str = get_server_address()
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Форма для изменения вопроса
    question_edit_form: QuestionEditForm = QuestionEditForm()

    # Получение данных о вопросе через REST API
    # Запрос
    response: requests.Response = request_session.get(f"{server_address}/api/v1/questions/{question_id}")

    # Обработка запроса
    if response:
        # Получение данных о вопросе
        question: dict = response.json()["question"]

        # Процесс редактирования вопроса (POST)
        if question_edit_form.validate_on_submit():
            # Чтение данных из формы
            name: str = clean_html(question_edit_form.name.data)
            tags: str = clean_html(question_edit_form.tags.data)
            content: str = clean_html(question_edit_form.content.data)

            # Обработка изображения
            image: FileStorage = question_edit_form.image.data
            if image:
                # Проверка на безопасность
                correct_extensions: str = question_edit_form.image.validators[0].upload_set
                is_safe, reason, secured_filename = Image.full_check(image.filename, correct_extensions, image.stream)

                if is_safe:
                    # Составление имени файла
                    file_extension: str = secured_filename.split(".")[-1]
                    filename: str = Image.full_clearing_filename(
                        f"{current_user.id}_{current_user.login}_{question_edit_form.name.data}.{file_extension}"
                    )
                else:
                    # Обработка ошибок
                    flash(reason, "error")
                    return redirect(url_for("question.edit", question_id=question_id))

            # Редактирование вопроса через REST API
            # Подготовка данных
            json_params: dict = {
                "name": name,
                "tags": tags,
                "content": content
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
                        remove_file(f"{Config.STATIC_URL_PATH}/questions_images/{question["image"]}")
                    # Сохранение изображения
                    image.save(f"{Config.STATIC_URL_PATH}/questions_images/{filename}")

                # Вывод сообщения
                flash("The question has been edited", "info")

                # Перенос на страницу с отредактированным вопросом
                return redirect(url_for("question.view", question_id=question_id))
            else:
                # Обработка ошибок
                ResponseErrorHandler.flash_reason_message(response)
        else:
            # Подстановка текущих данных в поля
            question_edit_form.name.data = question["name"]
            question_edit_form.tags.data = ", ".join([tag["name"] for tag in question["tags"]])
            question_edit_form.content.data = question["content"]

        # Отображение страницы (GET)
        return render_template(
            "question/edit.html",
            question_edit_form=question_edit_form,
            question=question
        )
    else:
        # Обработка ошибок
        ResponseErrorHandler.flash_reason_message(response)

    # Возвращение в меню, если вопрос не удалось загрузить
    return redirect(url_for("question.home"))


@bp.route("/<int:question_id>/delete", methods=["GET", "POST"])
@login_required
def delete(question_id: int):
    """Удаление вопроса"""

    # Подготовка данных для REST API
    server_address: str = get_server_address()
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Получение данных о вопросе через REST API
    # Запрос
    response: requests.Response = request_session.get(f"{server_address}/api/v1/questions/{question_id}")

    # Обработка запроса
    if response:
        # Получение данных о вопросе
        question: dict = response.json()["question"]

        # Удаление вопроса через REST API
        # Запрос
        response: requests.Response = request_session.delete(
            f"{server_address}/api/v1/questions/{question_id}",
            cookies=request.cookies
        )

        # Обработка запроса
        if response:
            # Удаление изображения
            if question["image"]: remove_file(f"{Config.STATIC_URL_PATH}/questions_images/{question["image"]}")

            # Вывод сообщения
            flash("Question deleted", "info")

            # Возвращение в меню
            return redirect(url_for("question.home"))
        else:
            # Обработка ошибок
            ResponseErrorHandler.flash_reason_message(response)
    else:
        # Обработка ошибок
        ResponseErrorHandler.flash_reason_message(response)

    # Возвращение на предыдущую страницу
    next_url: str = request.args.get("next", url_for("question.view", question_id=question_id))
    return redirect(next_url)


@bp.route("/<int:question_id>/delete/image", methods=["GET"])
@login_required
def delete_image(question_id: int):
    """Удаление изображения вопроса"""

    # Подготовка данных для REST API
    server_address: str = get_server_address()
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Получение данных о вопросе через REST API
    # Запрос
    response: requests.Response = request_session.get(f"{server_address}/api/v1/questions/{question_id}")

    # Обработка запроса
    if response:
        # Получение данных о вопросе
        question: dict = response.json()["question"]

        if question["image"]:
            # Удаление названия изображения вопроса через REST API
            # Подготовка данных
            json_params: dict = {
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
                remove_file(f"{Config.STATIC_URL_PATH}/questions_images/{question["image"]}")

                # Вывод сообщения
                flash("The question image has been deleted", "info")
            else:
                # Обработка ошибок
                ResponseErrorHandler.flash_reason_message(response)
    else:
        # Обработка ошибок
        ResponseErrorHandler.flash_reason_message(response)

    # Возвращение на предыдущую страницу
    next_url: str = request.args.get("next", url_for("question.edit", question_id=question_id))
    return redirect(next_url)


@bp.route("/<int:question_id>/solved/<string:solved_status>", methods=["GET"])
@login_required
def set_solved(question_id: int, solved_status: str):
    """Изменение состояния is_solved"""

    # Подготовка данных для REST API
    server_address: str = get_server_address()
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Изменение состояния is_solved через REST API
    # Подготовка данных
    json_params: dict = {
        "is_solved": solved_status == "true"
    }
    # Запрос
    response: requests.Response = request_session.put(
        f"{server_address}/api/v1/questions/{question_id}",
        json=json_params,
        cookies=request.cookies
    )

    # Обработка запроса
    if not response:
        # Обработка ошибок
        ResponseErrorHandler.flash_reason_message(response)

    # Возвращение на предыдущую страницу
    next_url: str = request.args.get("next", url_for("question.view", question_id=question_id))
    return redirect(next_url)


@bp.route("/<int:question_id>/closed/<string:closed_status>", methods=["GET"])
@login_required
def set_closed(question_id: int, closed_status: str):
    """Изменение состояния is_closed"""

    # Подготовка данных для REST API
    server_address: str = get_server_address()
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Изменение состояния is_closed через REST API
    # Подготовка данных
    json_params: dict = {
        "is_closed": closed_status == "true"
    }
    # Запрос
    response: requests.Response = request_session.put(
        f"{server_address}/api/v1/questions/{question_id}",
        json=json_params,
        cookies=request.cookies
    )

    # Обработка запроса
    if not response:
        # Обработка ошибок
        ResponseErrorHandler.flash_reason_message(response)

    # Возвращение на предыдущую страницу
    next_url: str = request.args.get("next", url_for("question.view", question_id=question_id))
    return redirect(next_url)


@bp.route("/search", methods=["GET", "POST"])
def search():
    """Поиск вопросов"""

    # Подготовка данных для REST API
    server_address: str = get_server_address()

    # Форма для поиска
    search_form: QuestionSearchForm = QuestionSearchForm()

    # Запрос на поиск через форму (POST)
    if search_form.validate_on_submit():
        # Чтение данных из формы
        filter_data: str = clean_html(search_form.search.data)

        # Обновление страницы с параметрами для поиска
        return redirect(url_for(
            "question.search",
            filter=filter_data,
            filter_mode="name"
        ))

    # Процесс поиска (параметры передаётся через параметры ссылки)
    found_questions: list[dict] = []
    # Получение данных из параметров ссылки
    filter_data: str | None = request.args.get("filter")
    filter_mode: str | None = request.args.get("filter_mode")
    if filter_data is not None and filter_mode is not None:
        # Очистка данных от HTML
        filter_data, filter_mode = clean_html(filter_data), clean_html(filter_mode)

        # Поиск вопросов через REST API
        # Подготовка данных
        json_params: dict = {
            "filter": filter_data,
            "filter_mode": filter_mode
        }
        # Запрос
        response = requests.get(
            f"{server_address}/api/v1/questions",
            json=json_params
        )

        # Обработка запроса
        if response:
            # Получение найденных вопросов
            found_questions = response.json()["questions"]
        else:
            # Обработка ошибок
            ResponseErrorHandler.flash_reason_message(response)

    # Отображение страницы без данных для поиска (GET)
    return render_template(
        "question/search.html",
        search_form=search_form,
        found_questions=found_questions
    )
