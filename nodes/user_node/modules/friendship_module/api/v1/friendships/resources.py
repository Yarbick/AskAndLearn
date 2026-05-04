"""REST API ресурсы"""

# Работа с фреймворком
from flask import jsonify, make_response

# Работа с REST API
import requests
from flask_restful import Resource

# Парсеры
from .parsers import FriendshipParsers

# Валидаторы
from .validators import FriendshipAborts, FriendshipValidators

# Работа с ORM
import sqlalchemy as sa
from nodes.user_node import db_manager
from nodes.user_node.data.models.friendship import Friendship


class FriendshipResource(Resource):
    """Ресурс одной дружбы"""

    def get(self, user_id: int, friend_id: int) -> requests.Response:
        """GET запрос для получения данных о дружбе"""

        # Получение дружбы из БД
        with db_manager.create_session() as db_session:
            friendship: Friendship | None = db_session.query(Friendship).filter(
                Friendship.user_id == user_id, Friendship.friend_id == friend_id
            ).first()
            # Проверки
            FriendshipValidators.is_exists(friendship)

            # Вывод результата
            return jsonify({"friendship": friendship.to_dict(only=[
                "user.id", "user.name", "user.icon", "friend.id", "friend.name", "friend.icon", "status",
                "last_changed_by"
            ])})

    def put(self, user_id: int, friend_id: int) -> requests.Response:
        """PUT запрос для изменения дружбы"""

        # Получение данных из парсера
        status: str = FriendshipParsers.put_parser.parse_args()["status"]

        # Изменение данных в БД (учитываются обе стороны)
        with db_manager.create_session() as db_session:
            # Получение дружбы из БД
            friendships: list[Friendship] = db_session.query(Friendship).filter(
                ((Friendship.user_id == user_id) & (Friendship.friend_id == friend_id)) |
                ((Friendship.friend_id == user_id) & (Friendship.user_id == friend_id))
            ).all()

            # Проверки
            FriendshipValidators.is_exists(friendships)
            for friendship in friendships: FriendshipValidators.is_available(friendship, next_status=status)

            # Изменение дружбы
            for friendship in friendships:
                friendship.last_changed_by = user_id
                friendship.status = status

            # Сохранение изменений
            db_session.commit()

            # Вывод результата
            return jsonify({"success": "OK"})

    def delete(self, user_id: int, friend_id: int) -> requests.Response:
        """DELETE запрос для удаления дружбы"""

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

    def get(self, user_id: int) -> requests.Response:
        """GET запрос для получения данных о дружбах пользователя"""

        # Получение данных из парсера
        parser_params: dict = FriendshipParsers.get_list_parser.parse_args()

        # Получение дружб из БД
        with db_manager.create_session() as db_session:
            if parser_params["filter"]:  # С фильтром
                if not parser_params["filter_mode"] or parser_params["filter_mode"] == "status":  # Фильтр по статусу
                    status: str = parser_params["filter"]
                    friendships: list[Friendship] = db_session.query(Friendship).filter(
                        Friendship.user_id == user_id,
                        Friendship.status == status,
                        sa.not_((Friendship.status == "blocked") & (Friendship.last_changed_by != user_id))
                    ).all()
            else:  # Без фильтра
                friendships: list[Friendship] = db_session.query(Friendship).filter(
                    Friendship.user_id == user_id,
                    sa.not_((Friendship.status == "blocked") & (Friendship.last_changed_by != user_id))
                ).all()

            # Вывод результата
            return jsonify({"friendships": [friendship.to_dict(only=[
                "friend.id", "friend.name", "friend.icon", "status", "last_changed_by"
            ]) for friendship in friendships]})

    def post(self, user_id: int) -> requests.Response:
        # Получение данных из парсера
        parser_data: dict = FriendshipParsers.post_parser.parse_args()

        # Добавление в БД (учитываются обе стороны)
        with db_manager.create_session() as db_session:
            # Проверки
            if db_session.query(Friendship).filter(
                    ((Friendship.user_id == user_id) & (Friendship.friend_id == parser_data["friend_id"])) |
                    ((Friendship.friend_id == user_id) & (Friendship.user_id == parser_data["friend_id"]))
            ).first(): FriendshipAborts.already_exist()
            FriendshipValidators.are_different_ids(user_id, parser_data["friend_id"])

            # Создание дружбы
            friendship_as_user: Friendship = Friendship(
                user_id=user_id, friend_id=parser_data["friend_id"], last_changed_by=user_id,
                status=parser_data["status"]
            )
            friendship_as_friend: Friendship = Friendship(
                user_id=parser_data["friend_id"], friend_id=user_id, last_changed_by=user_id,
                status=parser_data["status"]
            )

            # Добавление объектов из БД
            db_session.add(friendship_as_user)
            db_session.add(friendship_as_friend)
            db_session.commit()

            # Вывод результата
            return make_response(jsonify({"success": "OK"}), 201)
