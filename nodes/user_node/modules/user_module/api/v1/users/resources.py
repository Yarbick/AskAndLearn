"""REST API ресурсы user"""

# Работа с фреймворком
from flask import jsonify, make_response
# Работа с REST API
from flask_restful import Resource

# Парсеры
from .parsers import UserParsers

# Валидаторы
from .validators import UserAborts, UserValidators

# Работа с ORM
from user_node import db_manager
from user_node.data.models.user import User
from sqlalchemy.exc import IntegrityError


class UserResource(Resource):
    """Ресурс одного пользователя"""

    def get(self, user_id: int):
        # Получение пользователя из БД
        with db_manager.create_session() as db_session:
            user: User = db_session.get(User, user_id)
            # Проверки
            UserValidators.is_exists(user)

        # Вывод результата
        return jsonify({"user": user.to_dict(only=["id", "name", "login", "password", "description", "icon"])})

    def put(self, user_id: int):
        # Получение данных из парсера
        user_data: dict = UserParsers.put_parser.parse_args()
        user_password: str = user_data.pop("password", None)

        # Изменение данных в БД
        with db_manager.create_session() as db_session:
            try:
                # Получение пользователя из БД
                user: User = db_session.get(User, user_id)
                # Проверки
                UserValidators.is_exists(user)
                UserValidators.is_available(user)

                # Изменение пользователя
                for field_name, value in user_data.items():
                    if value is not None: setattr(user, field_name, value)
                if user_password: user.set_password(user_password)

                # Сохранение изменений
                db_session.commit()
            except IntegrityError:
                # Вызов ошибки, если пользователь с указанным логином уже существует
                UserAborts.login_exist()

            # Вывод результата
            return jsonify({"success": "OK"})

    def delete(self, user_id: int):
        # Удаление из БД
        with db_manager.create_session() as db_session:
            # Получение пользователя из БД
            user: User = db_session.get(User, user_id)
            # Проверки
            UserValidators.is_exists(user)
            UserValidators.is_available(user)

            # Удаление пользователя
            db_session.delete(user)
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})


class UserListResource(Resource):
    """Ресурс списка пользователей"""

    def get(self):
        # Получение данных из парсера
        filter_params = UserParsers.get_list_parser.parse_args()

        # Получение пользователей из БД
        with db_manager.create_session() as db_session:
            if filter_params["search"]:
                users: list[User] = db_session.query(User).filter(
                    User.name.ilike(f"%{filter_params["search"]}%") | User.login.ilike(f"%{filter_params["search"]}%")
                ).all()
            else:
                users: list[User] = db_session.query(User).all()

        # Вывод результата
        return jsonify({"users": [user.to_dict(only=["id", "name", "login", "icon"]) for user in users]})

    def post(self):
        # Получение данных из парсера
        user_data: dict = UserParsers.post_parser.parse_args()
        user_password: str = user_data.pop("password")

        # Добавление в БД
        with db_manager.create_session() as db_session:
            try:
                # Создание пользователя
                user = User()
                for field_name, value in user_data.items():
                    setattr(user, field_name, value)
                user.set_password(user_password)

                # Добавление объекта в БД
                db_session.add(user)
                db_session.commit()
            except IntegrityError:
                # Вызов ошибки, если пользователь с указанным логином уже существует
                UserAborts.login_exist()

            # Вывод результата
            return make_response(jsonify({"id": user.id}), 201)
