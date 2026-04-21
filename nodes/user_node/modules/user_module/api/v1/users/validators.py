"""Валидаторы для REST API user"""

# Работа с фреймворком
from flask_login import current_user

# Работа с REST API
from flask_restful import abort

# Работа с ORM
from user_node.data.models.user import User


class UserAborts:
    """Методы для вызова ошибок"""

    @staticmethod
    def not_found() -> None:
        """Пользователь не найден"""

        abort(404, error="User not found")

    @staticmethod
    def login_exist() -> None:
        """Пользователь с данным логином существует"""

        abort(400, error="The user with this login already exists")

    @staticmethod
    def unauthorized() -> None:
        """Пользователь не зарегистрирован"""

        abort(401, error="Unauthorized")

    @staticmethod
    def forbidden() -> None:
        """Нет доступа к аккаунту пользователя"""

        abort(403, error="Access is denied")


class UserValidators:
    """Методы для проверки"""

    @staticmethod
    def is_exists(user: User) -> None:
        """Проверка на существование пользователя"""

        if not user: UserAborts.not_found()

    @staticmethod
    def is_available(user: User) -> None:
        """Проверка на доступ к аккаунту пользователя"""

        if not current_user.is_authenticated: UserAborts.unauthorized()
        if user != current_user: UserAborts.forbidden()
