"""Валидаторы для REST API ресурса"""

# Работа с фреймворком
from flask_login import current_user

# Работа с REST API
from flask_restful import abort

# Работа с ORM
from qa_node.data.models.favorite import Favorite


class FavoriteAborts:
    """Методы для вызова ошибок"""

    @staticmethod
    def not_found() -> None:
        """Избранный вопрос не найден"""

        abort(404, error="Favorite not found")

    @staticmethod
    def unauthorized() -> None:
        """Пользователь не авторизован"""

        abort(403, error="Unauthorized")

    @staticmethod
    def forbidden() -> None:
        """Нет доступа к избранным пользователя"""

        abort(403, error="Forbidden")

    @staticmethod
    def already_exists():
        """Данный вопрос уже добавлен в избранные у пользователя"""

        abort(400, error="This question has already been added to the user's favorites")


class FavoriteValidators:
    """Методы для проверки"""

    @staticmethod
    def is_exists(favorite: Favorite) -> None:
        """Проверка на существование избранного вопроса"""

        if not favorite: FavoriteAborts.not_found()

    @staticmethod
    def is_available(favorite: Favorite) -> None:
        """Проверка на доступ к избранным"""

        # Проверка на авторизацию пользователя
        if not current_user.is_authenticated: FavoriteAborts.unauthorized()
        # Проверка на доступ к избранному вопросу
        if favorite.user_id != current_user.id: FavoriteAborts.forbidden()
