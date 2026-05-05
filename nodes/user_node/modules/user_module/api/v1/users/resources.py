"""REST API ресурсы"""

# Работа с фреймворком
from flask import jsonify, make_response, request

# Работа с REST API
import requests
from flask_restful import Resource

# Безопасность
from security.csrf import create_csrf_request_session
from security.rate_limiter import api_route_limits
from security.xss import clean_html

# Парсеры
from .parsers import UserParsers

# Валидаторы
from .validators import UserAborts, UserValidators

# Работа с ORM
from nodes.user_node import db_manager
from nodes.user_node.data.models.user import User


class UserResource(Resource):
    """Ресурс одного пользователя"""

    # Декораторы
    decorators = api_route_limits.copy()

    def get(self, user_id: int) -> requests.Response:
        """GET запрос для получения данных пользователя"""

        # Получение пользователя из БД
        with db_manager.create_session() as db_session:
            user: User | None = db_session.get(User, user_id)
            # Проверки
            UserValidators.is_exists(user)

            # Вывод результата
            return jsonify({"user": user.to_dict(only=["id", "name", "login", "password", "description", "icon"])})

    def put(self, user_id: int) -> requests.Response:
        """PUT запрос для изменения пользователя"""

        # Получение данных из парсера
        parser_data: dict = clean_html(UserParsers.put_parser.parse_args())
        user_password: str | None = parser_data.pop("password", None)

        # Изменение данных в БД
        with db_manager.create_session() as db_session:
            # Получение пользователя из БД
            user: User | None = db_session.get(User, user_id)
            # Проверки
            UserValidators.is_exists(user)
            UserValidators.is_available(user)
            UserValidators.are_very_long_fields(user)

            # Изменение пользователя
            for field_name, value in parser_data.items():
                if value is not None: setattr(user, field_name, value)
            # Изменение пароля
            if user_password:
                user.set_password(user_password)

            # Сохранение изменений
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})

    def delete(self, user_id: int) -> requests.Response:
        """DELETE запрос для удаления пользователя"""

        # Подготовка данных для REST API
        server_address: str = f"{request.scheme}://{request.host}"
        request_session: requests.Session = create_csrf_request_session(server_address)

        # Удаление из БД
        with db_manager.create_session() as db_session:
            # Получение пользователя из БД
            user: User | None = db_session.get(User, user_id)
            # Проверки
            UserValidators.is_exists(user)
            UserValidators.is_available(user)

            # Удаление связей с другими пользователями
            for friendship in set(user.friendships_as_user).union(user.friendships_as_friend):
                db_session.delete(friendship)

            # Удаление связей с вопросами и комментариями через REST API
            # Подготовка данных
            json_params: dict = {
                "creator_id": user_id
            }
            # Запросы
            request_session.patch(
                f"{server_address}/api/v1/questions",
                json=json_params,
                cookies=request.cookies
            )  # Удаление связей с вопросами
            request_session.patch(
                f"{server_address}/api/v1/comments",
                json=json_params,
                cookies=request.cookies
            )  # Удаление связей с комментариями

            # Очистка избранных через REST API
            # Подготовка данных
            json_params: dict = {
                "filter": user_id,
                "filter_mode": "user"
            }
            # Запросы
            request_session.delete(
                f"{server_address}/api/v1/favorites",
                json=json_params,
                cookies=request.cookies
            )

            # Удаление пользователя
            db_session.delete(user)
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})


class UserListResource(Resource):
    """Ресурс списка пользователей"""

    # Декораторы
    decorators = api_route_limits.copy()

    def get(self) -> requests.Response:
        """GET запрос для получения данных пользователей"""

        # Получение данных из парсера
        parser_data: dict = clean_html(UserParsers.get_list_parser.parse_args())

        # Получение пользователей из БД
        with db_manager.create_session() as db_session:
            if parser_data["filter"]:  # С фильтром
                if not parser_data["filter_mode"] or parser_data["filter_mode"] == "name-login":  # Фильтр по имени
                    name_or_login: str = parser_data["filter"]
                    users: list[User] = db_session.query(User).filter(
                        User.name.ilike(f"%{name_or_login}%") | User.login.ilike(f"%{name_or_login}%")
                    ).all()
            else:  # Без фильтра
                users: list[User] = db_session.query(User).all()

            # Вывод результата
            return jsonify({"users": [user.to_dict(only=["id", "name", "login", "icon"]) for user in users]})

    def post(self) -> requests.Response:
        """POST запрос для создания пользователя"""

        # Получение данных из парсера
        parser_data: dict = clean_html(UserParsers.post_parser.parse_args())
        user_password: str = parser_data.pop("password")

        # Добавление в БД
        with db_manager.create_session() as db_session:
            # Проверки
            if db_session.query(User).filter(User.login == parser_data["login"]).first(): UserAborts.login_exist()

            # Создание пользователя
            user: User = User()
            for field_name, value in parser_data.items():
                setattr(user, field_name, value)
            # Создание пароля
            user.set_password(user_password)
            # Проверки
            UserValidators.are_very_long_fields(user)

            # Добавление объекта в БД
            db_session.add(user)
            db_session.commit()

            # Вывод результата
            return make_response(jsonify({"id": user.id}), 201)
