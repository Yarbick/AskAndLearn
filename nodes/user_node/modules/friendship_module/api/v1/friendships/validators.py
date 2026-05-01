"""Валидаторы для REST API ресурса"""

# Работа с фреймворком
from flask_login import current_user

# Работа с REST API
from flask_restful import abort

# Работа с ORM
from user_node.data.models.friendship import Friendship


class FriendshipAborts:
    """Методы для вызова ошибок"""

    @staticmethod
    def not_found() -> None:
        """Дружба не найдена"""

        abort(404, error="Friendship not found")

    @staticmethod
    def already_exist() -> None:
        """Дружба между пользователями уже существует"""

        abort(400, error="Friendship between users already exists")

    @staticmethod
    def unauthorized() -> None:
        """Пользователь не зарегистрирован"""

        abort(401, error="Unauthorized")

    @staticmethod
    def forbidden() -> None:
        """Нет доступа к дружбе"""

        abort(403, error="Forbidden")

    @staticmethod
    def self_confirmation_attempt() -> None:
        """Пользователь заблокирован другим пользователем"""

        abort(400, error="You cannot confirm a self-friend request")

    @staticmethod
    def blocked() -> None:
        """Пользователь заблокирован другим пользователем"""

        abort(403, error="The user is blocked by another user")

    @staticmethod
    def equal_ids() -> None:
        """Одинаковые ID у пользователей"""

        abort(400, error="The user cannot be friends with himself")


class FriendshipValidators:
    """Методы для проверки"""

    @staticmethod
    def is_exists(friendship: Friendship | list[Friendship]) -> None:
        """Проверка на существование дружбы"""

        if not friendship: FriendshipAborts.not_found()

    @staticmethod
    def is_available(friendship: Friendship, next_status: str | None = None) -> None:
        """Проверка на доступ к дружбе"""

        if not current_user.is_authenticated: FriendshipAborts.unauthorized()
        if current_user.id not in (friendship.user_id, friendship.friend_id): FriendshipAborts.forbidden()
        if friendship.last_changed_by != current_user.id and friendship.status == "blocked":
            FriendshipAborts.blocked()
        if (next_status == "accepted" and friendship.last_changed_by == current_user.id
                and friendship.status == "pending"): FriendshipAborts.self_confirmation_attempt()

    @staticmethod
    def are_different_ids(user_id: int, friend_id: int) -> None:
        """Проверка на разность ID"""

        if user_id == friend_id: FriendshipAborts.equal_ids()
