"""Обработчики маршрутов модуля User"""

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
from .forms.edit import EditForm
from .forms.delete import DeleteForm
from .forms.search import SearchForm


@bp.route("/<int:user_id>/view", methods=["GET"])
def view(user_id: int):
    """Просмотр пользователя"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"

    # Получение данных о пользователе
    response = requests.get(f"{server_address}/api/v1/users/{user_id}")
    displayed_user: dict = response.json()["user"] if response else None

    # Получение данных о связи с текущим пользователем
    if current_user.is_authenticated and displayed_user:
        response = requests.get(f"{server_address}/api/v1/users/{current_user.id}/friendships/{user_id}")
        friendship = response.json()["friendship"] if response else None
    else:
        friendship = None

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
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Форма для редактирования профиля
    edit_form = EditForm()

    # Процесс редактирования профиля (POST)
    if edit_form.validate_on_submit():
        # Обработка иконки пользователя
        icon: FileStorage = edit_form.icon.data
        if icon:
            # Проверка на безопасность
            correct_extensions = edit_form.icon.validators[0].upload_set
            is_safe, reason, secured_filename = Image.full_check(icon.filename, correct_extensions, icon.stream)

            if is_safe:
                # Составление имени файла
                file_extension = secured_filename.split(".")[-1]
                filename = Image.full_clearing_filename(f"{current_user.id}_{current_user.login}.{file_extension}")
            else:
                flash(reason, "error")
                return redirect(url_for("user.edit"))

        # Сохранение имени файла для проверки
        icon_filename: str | None = current_user.icon

        # Изменение данных через REST API
        # Подготовка данных
        json_params = {
            "name": edit_form.name.data,
            "description": edit_form.description.data
        }
        if icon: json_params["icon"] = filename
        # Запрос
        response: requests.Response = request_session.put(
            f"{server_address}/api/v1/users/{current_user.id}",
            json=json_params,
            cookies=request.cookies
        )

        # Обработка запроса
        if response:
            if icon:
                # Удаление иконки
                if icon_filename:
                    remove_file(f"{Config.static_url_path}/users_icons/{icon_filename}")
                # Сохранение новой иконки
                icon.save(f"{Config.static_url_path}/users_icons/{filename}")

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
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Форма удаления пользователя
    delete_form = DeleteForm()

    # Удаление аккаунта (POST)
    if delete_form.validate_on_submit():
        # Проверка логина
        if current_user.login != delete_form.login.data:
            flash("Invalid login", "error")
            return redirect(url_for("user.delete"))
        # Проверка пароля
        if not current_user.check_password(delete_form.password.data):
            flash("Invalid password", "error")
            return redirect(url_for("user.delete"))
        # Проверка на подтверждение
        if not delete_form.accept_deleting.data:
            flash("Confirm the action", "error")
            return redirect(url_for("user.delete"))

        # Сохранение имени файла для проверки
        icon_filename: str | None = current_user.icon

        # Удаление пользователя через REST API
        # Запрос
        response: requests.Response = request_session.delete(
            f"{server_address}/api/v1/users/{current_user.id}",
            cookies=request.cookies
        )

        # Обработка запроса
        if response:
            # Удаление иконки
            if icon_filename:
                remove_file(f"{Config.static_url_path}/users_icons/{icon_filename}")

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
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Удаление названия иконки из БД через REST API
    # Подготовка данных
    json_params = {
        "icon": ""
    }
    # Запрос
    response = request_session.put(
        f"{server_address}/api/v1/users/{current_user.id}",
        json=json_params,
        cookies=request.cookies
    )

    # Обработка запроса
    if response:
        # Удаление иконки
        if current_user.icon:
            remove_file(f"{Config.static_url_path}/users_icons/{current_user.icon}")
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
    server_address = f"{request.scheme}://{request.host}"

    # Форма для поиска
    search_form = SearchForm()

    # Запрос на поиск через форму (POST)
    if search_form.validate_on_submit():
        # Обновление страницы с параметрами для поиска
        return redirect(url_for(
            "user.search",
            search=search_form.search.data,
            search_mode="name-login"
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
            f"{server_address}/api/v1/users",
            json=json_params
        )

        # Обработка запроса
        if response:
            # Получение данных
            found_users = response.json()["users"]

            # Отображение страницы (GET)
            return render_template(
                "user/search.html",
                search_form=search_form,
                found_users=found_users
            )
        else:
            # Обработка ошибок
            ResponseErrorHandler.flash_reason_message(response)

    # Отображение страницы без данных для поиска (GET)
    return render_template(
        "user/search.html",
        search_form=search_form
    )
