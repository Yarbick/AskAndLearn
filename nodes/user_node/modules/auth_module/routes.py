"""Обработчики маршрутов модуля Auth"""

# Работа с фреймворком
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_required, login_user, logout_user, current_user

# Подключение к модулю
from .blueprint import bp

# Работа с REST API
import requests

# Формы
from .forms.register import RegisterForm
from .forms.login import LoginForm

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
        server_address = f"{"https" if request.is_secure else "http"}://{request.host}"
        response = requests.post(
            f"{server_address}/api/v1/users",
            json={
                "name": register_form.name.data,
                "login": register_form.login.data,
                "password": register_form.password.data
            }
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
            # Вывод ошибки, если что-то пошло не так
            try:
                flash(response.json()["error"], "error")
            except:
                flash("Something went wrong", "error")
            return redirect(url_for("auth.register"))

    # Отображение страницы (GET)
    return render_template(
        "register.html",
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
        "login.html",
        login_form=login_form
    )


@bp.route("/logout", methods=["GET"])
@login_required
def logout():
    """Выход из аккаунта"""

    # Выход из аккаунта
    logout_user()
    # Переключение на главную страницу
    return redirect("/")
