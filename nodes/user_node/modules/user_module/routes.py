"""Обработчики маршрутов модуля"""

# Работа с фреймворком
from flask import render_template, url_for, redirect, request, flash

# Работа с пользователем
from flask_login import current_user, login_required

# Безопасность
from security.user import create_user_request_session
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

# Формы
from .forms.user.edit import EditForm
from .forms.user.delete import DeleteForm
from .forms.user.search import SearchForm


@bp.route("/<int:user_id>/view", methods=["GET"])
def view(user_id: int):
    """Просмотр пользователя"""

    # Подготовка данных для REST API
    server_address: str = get_server_address()

    # Получение данных о пользователе через REST API
    # Запрос
    response: requests.Response = requests.get(
        f"{server_address}/api/v1/users/{user_id}"
    )

    # Обработка запроса
    # Получение данных об отображаемом пользователе
    displayed_user: dict | None = response.json()["user"] if response else None

    # Получение данных о связи с текущим пользователем через REST API
    friendship: dict | None = None
    if current_user and current_user.is_authenticated and displayed_user:
        # Запрос
        response: requests.Response = requests.get(
            f"{server_address}/api/v1/users/{current_user.id}/friendships/{user_id}"
        )

        # Обработка запроса
        # Получение данных о связи с текущим пользователем
        friendship = response.json()["friendship"] if response else None

    # Отображение страницы (GET)
    return render_template(
        "user/view.html",
        displayed_user=displayed_user,
        friendship=friendship
    )


@bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    """Редактирование пользователя"""

    # Подготовка данных для REST API
    server_address: str = get_server_address()
    request_session: requests.Session = create_user_request_session(server_address)

    # Форма для редактирования профиля
    edit_form: EditForm = EditForm()

    # Процесс редактирования профиля (POST)
    if edit_form.validate_on_submit():
        # Чтение данных из формы
        name: str = clean_html(edit_form.name.data)
        description: str = clean_html(edit_form.description.data)

        # Обработка иконки пользователя
        icon: FileStorage = edit_form.icon.data
        if icon:
            # Проверка на безопасность
            correct_extensions: list[str] = edit_form.icon.validators[0].upload_set
            is_safe, reason, secured_filename = Image.full_check(icon.filename, correct_extensions, icon.stream)

            if is_safe:
                # Составление имени файла
                file_extension: str = secured_filename.split(".")[-1]
                new_icon_filename: str = Image.full_clearing_filename(
                    f"{current_user.id}_{current_user.login}.{file_extension}"
                )
            else:
                # Обработка ошибок
                flash(reason, "error")
                return redirect(url_for("user.edit"))

        # Сохранение имени файла для проверки
        old_icon_filename: str | None = current_user.icon

        # Изменение данных через REST API
        # Подготовка данных
        json_params: dict = {
            "name": name,
            "description": description
        }
        if icon: json_params["icon"] = new_icon_filename
        # Запрос
        response: requests.Response = request_session.put(
            f"{server_address}/api/v1/users/{current_user.id}",
            json=json_params
        )

        # Обработка запроса
        if response:
            # Обработка иконки
            if icon:
                # Удаление старой иконки
                if old_icon_filename: remove_file(f"{Config.STATIC_PATH}/users_icons/{old_icon_filename}")
                # Сохранение новой иконки
                icon.save(f"{Config.STATIC_PATH}/users_icons/{new_icon_filename}")

            # Вывод сообщения
            flash("Account settings have been changed", "info")

            # Возвращение на страницу профиля
            return redirect(url_for("user.view", user_id=current_user.id))
        else:
            # Обработка ошибок
            ResponseErrorHandler.flash_reason_message(response)
            return redirect(url_for("user.edit"))

    # Отображение существующих данных пользователя
    edit_form.name.data = current_user.name
    edit_form.description.data = current_user.description

    # Отображение страницы (GET)
    return render_template(
        "user/edit.html",
        edit_form=edit_form
    )


@bp.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    """Удаление пользователя"""

    # Подготовка данных для REST API
    server_address: str = get_server_address()
    request_session: requests.Session = create_user_request_session(server_address)

    # Форма удаления пользователя
    delete_form: DeleteForm = DeleteForm()

    # Удаление аккаунта (POST)
    if delete_form.validate_on_submit():
        # Чтение данных из формы
        login: str = clean_html(delete_form.login.data)
        password: str = clean_html(delete_form.password.data)
        accepted: bool = delete_form.accept_deleting.data

        # Проверка логина
        if current_user.login != login:
            flash("Invalid login", "error")
            return redirect(url_for("user.delete"))
        # Проверка пароля
        if not current_user.check_password(password):
            flash("Invalid password", "error")
            return redirect(url_for("user.delete"))
        # Проверка на подтверждение
        if not accepted:
            flash("Confirm the action", "error")
            return redirect(url_for("user.delete"))

        # Сохранение имени файла для проверки
        icon_filename: str | None = current_user.icon

        # Удаление пользователя через REST API
        # Запрос
        response: requests.Response = request_session.delete(
            f"{server_address}/api/v1/users/{current_user.id}"
        )

        # Обработка запроса
        if response:
            # Удаление иконки
            if icon_filename: remove_file(f"{Config.STATIC_PATH}/users_icons/{icon_filename}")

            # Вывод сообщения
            flash("Account deleted", "info")

            # Выход из аккаунта
            return redirect(url_for("auth.logout"))
        else:
            # Обработка ошибок
            ResponseErrorHandler.flash_reason_message(response)

    # Отображение страницы (GET)
    return render_template(
        "user/delete.html",
        delete_form=delete_form
    )


@bp.route("/delete/icon", methods=["GET"])
@login_required
def delete_icon():
    """Удаление иконки пользователя"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_user_request_session(server_address)

    # Удаление названия иконки из БД через REST API
    # Подготовка данных
    json_params: dict = {
        "icon": ""
    }
    # Запрос
    response: requests.Response = request_session.put(
        f"{server_address}/api/v1/users/{current_user.id}",
        json=json_params
    )

    # Обработка запроса
    if response:
        # Удаление иконки
        if current_user.icon: remove_file(f"{Config.STATIC_PATH}/users_icons/{current_user.icon}")

        # Вывод сообщения
        flash("The icon has been deleted", "info")
    else:
        # Обработка ошибок
        ResponseErrorHandler.flash_reason_message(response)

    # Возвращение на предыдущую страницу
    next_url: str = request.args.get("next", url_for("user.edit"))
    return redirect(next_url)


@bp.route("/search", methods=["GET", "POST"])
def search():
    """Поиск пользователей"""

    # Подготовка данных для REST API
    server_address: str = get_server_address()

    # Форма для поиска
    search_form: SearchForm = SearchForm()

    # Запрос на поиск через форму (POST)
    if search_form.validate_on_submit():
        # Чтение данных из формы
        filter_data: str = clean_html(search_form.search.data)

        # Обновление страницы с параметрами для поиска
        return redirect(url_for(
            "user.search",
            filter=filter_data,
            filter_mode="name-login"
        ))

    # Процесс поиска (параметры передаётся через параметры ссылки)
    found_users: list = []
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
        response: requests.Response = requests.get(
            f"{server_address}/api/v1/users",
            json=json_params
        )

        # Обработка запроса
        if response:
            # Получение найденных пользователей
            found_users: list[dict] = response.json()["users"]
        else:
            # Обработка ошибок
            ResponseErrorHandler.flash_reason_message(response)

    # Отображение страницы (GET)
    return render_template(
        "user/search.html",
        search_form=search_form,
        found_users=found_users
    )
