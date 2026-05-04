"""Обработчики маршрутов модуля"""

# Работа с фреймворком
from flask import render_template, url_for, flash, redirect, request, session as flask_session

# Работа с пользователем
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
from .forms.auth.register import RegisterForm
from .forms.auth.login import LoginForm
from .forms.auth.change_password import ChangePasswordForm

# Работа с ORM
from nodes.user_node import db_manager
from nodes.user_node.data.models.user import User


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Регистрация"""

    # Подготовка данных для REST API
    server_address: str = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Форма для регистрации
    register_form: RegisterForm = RegisterForm()

    # Процесс регистрации (POST)
    if register_form.validate_on_submit():
        # Проверка на совпадение паролей
        if register_form.password.data != register_form.repeat_password.data:
            flash("Passwords don't match", "error")
            return redirect(url_for("auth.register"))

        # Создание пользователя через REST API
        # Подготовка данных
        json_params: dict = {
            "name": register_form.name.data,
            "login": register_form.login.data,
            "password": register_form.password.data
        }
        # Запрос
        response: requests.Response = request_session.post(
            f"{server_address}/api/v1/users",
            json=json_params
        )

        # Обработка запроса
        if response:
            # Получение объекта пользователя
            user_id: int = response.json()["id"]
            with db_manager.create_session() as db_session:
                user: User | None = db_session.get(User, user_id)

            if user:
                # Вход в аккаунт
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

    # Форма для авторизации
    login_form: LoginForm = LoginForm()

    # Процесс авторизации (POST)
    if login_form.validate_on_submit():
        with db_manager.create_session() as db_session:
            # Получение пользователя
            user: User | None = db_session.query(User).filter(User.login == login_form.login.data).first()

            # Проверка на существование пользователя
            if not user:
                flash("Invalid login", "error")
                return redirect(url_for("auth.login"))
            # Проверка пароля
            if not user.check_password(login_form.password.data):
                flash("Invalid password", "error")
                return redirect(url_for("auth.login"))

            # Вход в аккаунт
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
    server_address: str = f"{request.scheme}://{request.host}"
    request_session: requests.Session = create_csrf_request_session(server_address)

    # Форма для изменения пароля
    change_password_form: ChangePasswordForm = ChangePasswordForm()

    # Процесс изменения пароля (POST)
    if change_password_form.validate_on_submit():
        # Проверка логина
        if not current_user.login == change_password_form.login.data:
            flash("Invalid login", "error")
            return redirect(url_for("auth.change_password"))
        # Проверка пароля
        if not current_user.check_password(change_password_form.old_password.data):
            flash("Invalid password", "error")
            return redirect(url_for("auth.change_password"))
        # Проверка на совпадение новых паролей
        if change_password_form.new_password.data != change_password_form.repeat_new_password.data:
            flash("New passwords don't match", "error")
            return redirect(url_for("auth.change_password"))

        # Изменение пароля через REST API
        # Подготовка данных
        json_params: dict = {
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
            # Вывод сообщения
            flash("The password has been changed", "info")

            # Возвращение на предыдущую страницу
            next_url: str = request.args.get("next", url_for("user.edit"))
            return redirect(next_url)
        else:
            # Обработка ошибок
            ResponseErrorHandler.flash_reason_message(response)
            return redirect(url_for("auth.change_password"))

    # Отображение страницы (GET)
    return render_template(
        "auth/change_password.html",
        change_password_form=change_password_form
    )
