"""Обработчики маршрутов модуля"""

# Работа с фреймворком
from flask import render_template, url_for, flash, redirect, request, session as flask_session

# Работа с пользователем
from flask_login import login_required, login_user, logout_user, current_user

# Подключение к модулю
from .blueprint import bp

# Настройки приложения
from app.config import get_server_address

# Безопасность
from security.user import create_user_request_session
from security.rate_limiter import limiter
from security.xss import clean_html
from secrets import token_urlsafe

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

# Работа с кешем
from cache.cacher import CacheManager


def generate_auth_token(user_id: int) -> str:
    """Генерация токена для авторизации пользователя"""

    # Генерация токена
    raw_token: str = token_urlsafe(32)

    # Сохранение токена в кеш для авторизации пользователя
    CacheManager.set(raw_token, user_id)

    # Возвращение токена
    return raw_token


@bp.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def register():
    """Регистрация"""

    # Подготовка данных для REST API
    server_address: str = get_server_address()

    # Форма для регистрации
    register_form: RegisterForm = RegisterForm()

    # Процесс регистрации (POST)
    if register_form.validate_on_submit():
        # Чтение данных из формы
        name: str = clean_html(register_form.name.data)
        login_: str = clean_html(register_form.login.data)
        password: str = clean_html(register_form.password.data)
        repeat_password: str = clean_html(register_form.repeat_password.data)
        remember_me: bool = register_form.remember_me.data

        # Проверка на совпадение паролей
        if password != repeat_password:
            flash("Passwords don't match", "error")
            return redirect(url_for("auth.register"))

        # Создание пользователя через REST API
        # Подготовка данных
        json_params: dict = {
            "name": name,
            "login": login_,
            "password": password
        }
        # Запрос
        response: requests.Response = requests.post(
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
                login_user(user, remember=remember_me)

                # Создание токена аутентификации для обращения к API
                auth_token: str = generate_auth_token(user.id)
                flask_session["auth_token"] = auth_token

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
@limiter.limit("10 per minute")
def login():
    """Авторизация"""

    # Форма для авторизации
    login_form: LoginForm = LoginForm()

    # Процесс авторизации (POST)
    if login_form.validate_on_submit():
        with db_manager.create_session() as db_session:
            # Чтение данных из формы
            login_: str = clean_html(login_form.login.data)
            password: str = clean_html(login_form.password.data)
            remember_me: bool = login_form.remember_me.data

            # Получение пользователя
            user: User | None = db_session.query(User).filter(User.login == login_).first()

            # Проверка на существование пользователя
            if not user:
                flash("Invalid login", "error")
                return redirect(url_for("auth.login"))
            # Проверка пароля
            if not user.check_password(password):
                flash("Invalid password", "error")
                return redirect(url_for("auth.login"))

            # Вход в аккаунт
            login_user(user, remember=remember_me)

            # Создание токена аутентификации для обращения к API
            auth_token: str = generate_auth_token(user.id)
            flask_session["auth_token"] = auth_token

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

    # Удаление хэша авторизации
    CacheManager.delete(flask_session.get("auth_token"))

    # Удаление cookie-сессий
    flask_session.clear()

    # Выход из аккаунта
    logout_user()

    # Переключение на главную страницу
    return redirect("/")


@bp.route("/change_password", methods=["GET", "POST"])
@login_required
@limiter.limit("10 per minute")
def change_password():
    """Изменение пароля"""

    # Подготовка данных для REST API
    server_address: str = get_server_address()
    request_session: requests.Session = create_user_request_session()

    # Форма для изменения пароля
    change_password_form: ChangePasswordForm = ChangePasswordForm()

    # Процесс изменения пароля (POST)
    if change_password_form.validate_on_submit():
        # Чтение данных из формы
        login_: str = clean_html(change_password_form.login.data)
        old_password: str = clean_html(change_password_form.old_password.data)
        new_password: str = clean_html(change_password_form.new_password.data)
        repeat_new_password: str = clean_html(change_password_form.repeat_new_password.data)

        # Проверка логина
        if not current_user.login == login_:
            flash("Invalid login", "error")
            return redirect(url_for("auth.change_password"))
        # Проверка пароля
        if not current_user.check_password(old_password):
            flash("Invalid password", "error")
            return redirect(url_for("auth.change_password"))
        # Проверка на совпадение новых паролей
        if new_password != repeat_new_password:
            flash("New passwords don't match", "error")
            return redirect(url_for("auth.change_password"))

        # Изменение пароля через REST API
        # Подготовка данных
        json_params: dict = {
            "password": new_password
        }
        # Запрос
        response: requests.Response = request_session.put(
            f"{server_address}/api/v1/users/{current_user.id}",
            json=json_params
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
