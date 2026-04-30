"""Обработчики маршрутов модуля Auth"""

# Работа с фреймворком
from flask import render_template, url_for, flash, redirect, request, session as flask_session
from flask_login import login_required, login_user, logout_user, current_user

# Подключение к модулю
from .blueprint import bp

# Безопасность
from security.csrf import create_csrf_request_session

# Обработка ошибок
from exceptions.api.rest.shared import ResponseErrorHandler

# Работа с REST API
import requests

# Формы
from .forms.register import RegisterForm
from .forms.login import LoginForm
from .forms.change_password import ChangePasswordForm

# Работа с ORM
from user_node import db_manager
from user_node.data.models.user import User


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Регистрация"""

    # Форма для регистрации
    register_form = RegisterForm()

    # Процесс регистрации (POST)
    if register_form.validate_on_submit():
        # Проверка на совпадение паролей
        if register_form.password.data != register_form.repeat_password.data:
            flash("Passwords don't match", "error")
            return redirect(url_for("auth.register"))

        # Создание пользователя через REST API
        # Подготовка данных
        server_address = f"{request.scheme}://{request.host}"
        request_session: requests.Session = create_csrf_request_session(server_address)
        json_params = {
            "name": register_form.name.data,
            "login": register_form.login.data,
            "password": register_form.password.data
        }
        # Запрос
        response: requests.Response = request_session.post(
            f"{server_address}/api/v1/users",
            json=json_params
        )

        # Вход в созданный аккаунт
        if response:
            # Получение объекта пользователя
            user_id = response.json()["id"]
            with db_manager.create_session() as db_session:
                user = db_session.get(User, user_id)

            # Вход
            login_user(user, remember=register_form.remember_me.data)
            # Переключение на главную страницу
            return redirect("/")
        else:
            # Обработка ошибок
            ResponseErrorHandler.flash_reason_message(response)
            return redirect(url_for("auth.register"))

    # Отображение страницы (GET)
    return render_template(
        "auth/register.html",
        register_form=register_form
    )


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Авторизация"""

    login_form = LoginForm()

    # Процесс авторизации (POST)
    if login_form.validate_on_submit():
        with db_manager.create_session() as db_session:
            # Получение пользователя
            user = db_session.query(User).filter(User.login == login_form.login.data).first()

            # Проверка на существование пользователя
            if not user:
                flash("Invalid login", "error")
                return redirect(url_for("auth.login"))
            # Проверка на совпадение паролей
            if not user.check_password(login_form.password.data):
                flash("Invalid password", "error")
                return redirect(url_for("auth.login"))

            # Вход
            login_user(user, remember=login_form.remember_me.data)
            # Переключение на главную страницу
            return redirect("/")

    # Отображение страницы (GET)
    return render_template(
        "auth/login.html",
        login_form=login_form
    )


@bp.route("/logout", methods=["GET"])
def logout():
    """Выход из аккаунта"""

    # Удаление cookie-сессий
    flask_session.clear()

    # Выход из аккаунта
    logout_user()

    # Переключение на главную страницу
    return redirect("/")


@bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Изменение пароля"""

    # Подготовка данных для REST API
    server_address = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Форма для изменения пароля
    change_password_form = ChangePasswordForm()

    # Процесс изменения пароля (POST)
    if change_password_form.validate_on_submit():
        # Проверка на совпадение логинов
        if not current_user.login == change_password_form.login.data:
            flash("Invalid login", "error")
            return redirect(url_for("auth.change_password"))
        # Проверка на совпадение паролей
        if not current_user.check_password(change_password_form.old_password.data):
            flash("Invalid password", "error")
            return redirect(url_for("auth.change_password"))
        # Проверка на совпадение новых паролей
        if change_password_form.new_password.data != change_password_form.repeat_new_password.data:
            flash("New passwords don't match", "error")
            return redirect(url_for("auth.change_password"))

        # Изменение пароля через REST API
        json_params = {
            "password": change_password_form.new_password.data
        }
        # Запрос
        response: requests.Response = request_session.put(
            f"{server_address}/api/v1/users/{current_user.id}",
            json=json_params,
            cookies=request.cookies
        )

        # Проверка на успешность выполнения
        if response:
            # Возвращение на страницу редактирования профиля пользователя
            return redirect(url_for("user.edit"))
        else:
            # Обработка ошибок
            ResponseErrorHandler.flash_reason_message(response)
            return redirect(url_for("auth.change_password"))

    # Отображение страницы (GET)
    return render_template(
        "auth/change_password.html",
        change_password_form=change_password_form
    )
