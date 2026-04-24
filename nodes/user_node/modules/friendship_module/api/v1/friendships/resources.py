"""REST API ресурсы friendships"""

# Работа с фреймворком
from flask import jsonify, make_response
from flask_login import current_user
# Работа с REST API
from flask_restful import Resource

# Парсеры
from .parsers import FriendshipParsers

# Валидаторы
from .validators import FriendshipAborts, FriendshipValidators, FriendshipStatusValidators

# Работа с ORM
import sqlalchemy as sa
from user_node import db_manager
from user_node.data.models.friendship import Friendship
from user_node.data.models.friendship_status import FriendshipStatus


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
            return jsonify({"friendship": friendship.to_dict(only=[
                "user.id", "user.name", "user.icon", "friend.id", "friend.name", "friend.icon", "status",
                "last_changed_by"
            ])})

    def put(self, user_id: int, friend_id: int):
        # Получение данных из парсера
        friendship_data: dict = FriendshipParsers.put_parser.parse_args()

        # Изменение данных в БД (учитываются обе стороны)
        with db_manager.create_session() as db_session:
            # Получение дружбы из БД
            friendships: list[Friendship] = db_session.query(Friendship).filter(
                ((Friendship.user_id == user_id) & (Friendship.friend_id == friend_id)) |
                ((Friendship.friend_id == user_id) & (Friendship.user_id == friend_id))
            ).all()
            # Получение статуса
            status = db_session.query(FriendshipStatus).filter(
                FriendshipStatus.name == friendship_data["status"]).first()

            # Проверки
            FriendshipValidators.is_exists(friendships)
            for friendship in friendships: FriendshipValidators.is_available(friendship, next_status=status.name)
            FriendshipStatusValidators.is_exists(status)

            # Изменение дружбы
            for friendship in friendships:
                friendship.last_changed_by = user_id
                friendship.status_id = status.id

            # Сохранение изменений
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})

    def delete(self, user_id: int, friend_id: int):
        # Удаление из БД (учитываются обе стороны)
        with db_manager.create_session() as db_session:
            # Получение дружбы из БД
            friendships: list[Friendship] = db_session.query(Friendship).filter(
                ((Friendship.user_id == user_id) & (Friendship.friend_id == friend_id)) |
                ((Friendship.friend_id == user_id) & (Friendship.user_id == friend_id))
            ).all()

            # Проверки
            FriendshipValidators.is_exists(friendships)
            for friendship in friendships: FriendshipValidators.is_available(friendship)

            # Удаление дружбы
            for friendship in friendships: db_session.delete(friendship)
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})


class FriendshipListResource(Resource):
    """Ресурс списка друзей у пользователя"""

    def get(self, user_id: int):
        # Получение данных из парсера
        filter_params = FriendshipParsers.get_list_parser.parse_args()

        # Получение дружб из БД
        with db_manager.create_session() as db_session:
            friendships: list[Friendship] = db_session.query(Friendship).join(Friendship.status).filter(
                Friendship.user_id == user_id,
                FriendshipStatus.name.in_(filter_params["status"]),
                sa.not_((FriendshipStatus.name == "blocked") & (Friendship.last_changed_by != user_id))
            ).all()

            # Вывод результата
            return jsonify({"friendships": [friendship.to_dict(only=[
                "friend.id", "friend.name", "friend.icon", "status.name", "last_changed_by"
            ]) for friendship in friendships]})

    def post(self, user_id: int):
        # Получение данных из парсера
        friendship_data: dict = FriendshipParsers.post_parser.parse_args()

        # Добавление в БД (учитываются обе стороны)
        with db_manager.create_session() as db_session:
            # Получение статуса
            status = db_session.query(FriendshipStatus).filter(
                FriendshipStatus.name == friendship_data["status"]).first()

            # Проверки
            if db_session.query(Friendship).filter(
                    ((Friendship.user_id == user_id) & (Friendship.friend_id == friendship_data["friend_id"])) |
                    ((Friendship.friend_id == user_id) & (Friendship.user_id == friendship_data["friend_id"]))
            ).first():
                FriendshipAborts.already_exist()
            FriendshipValidators.are_different_ids(user_id, friendship_data["friend_id"])
            FriendshipStatusValidators.is_exists(status)

            # Создание дружбы
            friendship_as_user = Friendship(
                user_id=user_id, friend_id=friendship_data["friend_id"], last_changed_by=user_id, status_id=status.id
            )
            friendship_as_friend = Friendship(
                user_id=friendship_data["friend_id"], friend_id=user_id, last_changed_by=user_id, status_id=status.id
            )

            # Добавление объекта в БД
            db_session.add(friendship_as_user)
            db_session.add(friendship_as_friend)
            db_session.commit()

            # Вывод результата
            return make_response(jsonify({"success": "OK"}), 201)
