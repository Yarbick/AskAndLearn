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
from .forms.profile_edit import ProfileEditForm
from .forms.delete import DeleteForm
from .forms.search import SearchForm


@bp.route("/<int:user_id>/profile", methods=["GET"])
def profile(user_id: int):
    """Профиль пользователя"""

    # Получение данных о пользователе
    server_address = f"{"https" if request.is_secure else "http"}://{request.host}"
    response = requests.get(f"{server_address}/api/v1/users/{user_id}")
    displayed_user: dict = response.json()["user"] if response else None

    # Отображение страницы (GET)
    return render_template(
        "profile.html",
        displayed_user=displayed_user
    )


@bp.route("/profile_edit", methods=["GET", "POST"])
@login_required
def profile_edit():
    """Редактирование профиля пользователя"""

    # Форма для редактирования профиля
    profile_edit_form = ProfileEditForm()

    # Процесс редактирования профиля (POST)
    if profile_edit_form.validate_on_submit():
        # Обработка иконки пользователя
        icon: FileStorage = profile_edit_form.icon.data
        if icon:
            # Проверка на безопасность
            correct_extensions = profile_edit_form.icon.validators[0].upload_set
            is_safe, reason, secured_filename = Image.full_check(icon.filename, correct_extensions, icon.stream)

            if is_safe:
                # Сохранение файла
                file_extension = secured_filename.split(".")[-1]
                filename = f"{current_user.id}_{current_user.login}.{file_extension}"
                icon.save(f"{Config.static_url_path}/users_icons/{filename}")
            else:
                flash(reason, "error")
                return redirect(url_for("user.profile_edit"))

        # Изменение данных через REST API
        # Подготовка данных
        server_address = f"{"https" if request.is_secure else "http"}://{request.host}"
        request_session: requests.Session = create_csrf_request_session(server_address)
        json_params = {
            "name": profile_edit_form.name.data,
            "description": profile_edit_form.description.data
        }
        if icon: json_params["icon"] = filename
        # Запрос
        response: requests.Response = request_session.put(
            f"{server_address}/api/v1/users/{current_user.id}",
            json=json_params,
            cookies=request.cookies
        )

        # Проверка на успешность выполнения
        if response:
            # Возвращение на страницу профиля
            return redirect(url_for("user.profile", user_id=current_user.id))
        else:
            # Вывод ошибки, если что-то пошло не так
            try:
                flash(response.json()["error"], "error")
            except:
                flash("Something went wrong", "error")
            return redirect(url_for("user.profile_edit"))

    # Отображение существующих данных пользователя
    profile_edit_form.name.data = current_user.name
    profile_edit_form.description.data = current_user.description

    # Проверка на правильное расширение файла (если обнаружила форма)
    if profile_edit_form.icon.errors:
        for error in profile_edit_form.icon.errors:
            flash(error, "error")
        return redirect(url_for("user.profile_edit"))

    # Отображение страницы (GET)
    return render_template(
        "profile_edit.html",
        profile_edit_form=profile_edit_form
    )


@bp.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    """Удаление пользователя"""

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

        # Удаление пользователя через REST API
        # Подготовка данных
        server_address = f"{"https" if request.is_secure else "http"}://{request.host}"
        request_session: requests.Session = create_csrf_request_session(server_address)
        # Запрос
        response: requests.Response = request_session.delete(
            f"{server_address}/api/v1/users/{current_user.id}",
            cookies=request.cookies
        )

        # Проверка на успешность выполнения
        if response:
            # Удаление иконки
            if current_user.icon:
                remove_file(f"{Config.static_url_path}/users_icons/{current_user.icon}")

            # Выход из аккаунта
            return redirect(url_for("auth.logout"))
        else:
            # Вывод ошибки, если что-то пошло не так
            try:
                flash(response.json()["error"], "error")
            except:
                flash("Something went wrong", "error")
            return redirect(url_for("user.delete"))

    # Отображение страницы (GET)
    return render_template(
        "delete.html",
        delete_form=delete_form
    )


@bp.route("/profile_edit/delete_icon", methods=["GET"])
@login_required
def delete_icon():
    """Удаление иконки"""

    # Удаление файла с иконкой
    if current_user.icon:
        remove_file(f"{Config.static_url_path}/users_icons/{current_user.icon}")

    # Удаление названия иконки из БД через REST API
    # Подготовка данных
    server_address = f"{"https" if request.is_secure else "http"}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)
    json_params = {
        "icon": ""
    }
    # Запрос
    request_session.put(
        f"{server_address}/api/v1/users/{current_user.id}",
        json=json_params,
        cookies=request.cookies
    )

    # Возвращение к редактированию профиля
    return redirect(url_for("user.profile_edit"))


@bp.route("/search", methods=["GET", "POST"])
def search():
    """Поиск пользователей"""

    # Форма для поиска пользователей
    search_form = SearchForm()

    # Поиск (POST)
    if search_form.validate_on_submit():
        # Поиск пользователей через REST API
        # Подготовка данных
        server_address = f"{"https" if request.is_secure else "http"}://{request.host}"
        json_params = {
            "search": search_form.search.data
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

            # Отображение страницы (POST)
            return render_template(
                "search.html",
                search_form=search_form,
                found_users=found_users
            )

        # Отображение страницы в случае ошибки (GET)
        flash(response.reason, "error")
        return redirect(
            "user.search"
        )

    # Отображение страницы (GET)
    return render_template(
        "search.html",
        search_form=search_form
    )
