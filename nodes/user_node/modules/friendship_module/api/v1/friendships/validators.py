"""Валидаторы для REST API friendships"""

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

        abort(403, error="Access is denied")


class FriendshipValidators:
    """Методы для проверки"""

    @staticmethod
    def is_exists(friendship: Friendship) -> None:
        """Проверка на существование дружбы"""

        if not friendship: FriendshipAborts.not_found()

    @staticmethod
    def is_available(friendship: Friendship) -> None:
        """Проверка на доступ к дружбе"""

        if not current_user.is_authenticated: FriendshipAborts.unauthorized()
        if friendship.user_id != current_user.id: FriendshipAborts.forbidden()
