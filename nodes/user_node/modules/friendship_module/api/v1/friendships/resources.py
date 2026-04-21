"""REST API ресурсы friendships"""

# Работа с фреймворком
from flask import jsonify, make_response
# Работа с REST API
from flask_restful import Resource

# Парсеры
from .parsers import FriendshipParsers

# Валидаторы
from .validators import FriendshipAborts, FriendshipValidators

# Работа с ORM
from user_node import db_manager
from user_node.data.models.friendship import Friendship


class FriendshipResource(Resource):
    """Ресурс одной дружбы"""

    def get(self, user_id: int, friend_id: int):
        # Получение дружбы из БД
        with db_manager.create_session() as db_session:
            friendship: Friendship = db_session.query(Friendship).filter(
                Friendship.user_id == user_id, Friendship.friend_id == friend_id
            ).first()
            # Проверки
            FriendshipValidators.is_exists(friendship)

        # Вывод результата
        return jsonify({"friendship": friendship.to_dict(only=["user_id", "friend_id", "status"])})

    def put(self, user_id: int, friend_id: int):
        # Получение данных из парсера
        friendship_data: dict = FriendshipParsers.put_parser.parse_args()

        # Изменение данных в БД
        with db_manager.create_session() as db_session:
            # Получение дружбы из БД
            friendship: Friendship = db_session.query(Friendship).filter(
                Friendship.user_id == user_id, Friendship.friend_id == friend_id
            ).first()
            # Проверки
            FriendshipValidators.is_exists(friendship)
            FriendshipValidators.is_available(friendship)

            # Изменение дружбы
            for field_name, value in friendship_data.items():
                if value is not None: setattr(friendship, field_name, value)

            # Сохранение изменений
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})

    def delete(self, user_id: int, friend_id: int):
        # Удаление из БД
        with db_manager.create_session() as db_session:
            # Получение дружбы из БД
            friendship: Friendship = db_session.query(Friendship).filter(
                Friendship.user_id == user_id, Friendship.friend_id == friend_id
            ).first()
            # Проверки
            FriendshipValidators.is_exists(friendship)
            FriendshipValidators.is_available(friendship)

            # Удаление дружбы
            db_session.delete(friendship)
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})


class FriendshipListResource(Resource):
    """Ресурс списка друзей у пользователя"""

    def get(self, user_id: int):
        # Получение дружб из БД
        with db_manager.create_session() as db_session:
            friendships: list[Friendship] = db_session.query(Friendship).filter(Friendship.user_id == user_id).all()

        # Вывод результата
        return jsonify({"friendships": [friendsh.to_dict(only=["friend_id", "status"]) for friendsh in friendships]})

    def post(self, user_id: int):
        # Получение данных из парсера
        friendship_data: dict = FriendshipParsers.post_parser.parse_args()

        # Добавление в БД
        with db_manager.create_session() as db_session:
            # Проверка на наличие дружбы между пользователями
            if db_session.query(Friendship).filter(
                    Friendship.user_id == user_id, Friendship.friend_id == friendship_data["friend_id"]).first():
                FriendshipAborts.already_exist()

            # Создание дружбы
            friendship = Friendship(
                user_id=user_id,
                friend_id=friendship_data["friend_id"],
                status=friendship_data["status"]
            )

            # Добавление объекта в БД
            db_session.add(friendship)
            db_session.commit()

            # Вывод результата
            return make_response(jsonify({"id": friendship.id}), 201)
