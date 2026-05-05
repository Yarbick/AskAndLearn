"""Валидаторы для REST API ресурса"""

# Работа с пользователем
from flask_login import current_user

# Работа с REST API
from flask_restful import abort

# Работа с ORM
from nodes.qa_node.data.models.favorite import Favorite
from nodes.qa_node.data.models.question import Question


class FavoriteAborts:
    """Методы для вызова ошибок"""

    @staticmethod
    def favorite_not_found() -> None:
        """Избранный вопрос не найден"""

        abort(404, error="Favorite not found")

    @staticmethod
    def question_not_found() -> None:
        """Вопрос не найден"""

        abort(404, error="Question not found")

    @staticmethod
    def unauthorized() -> None:
        """Пользователь не авторизован"""

        abort(403, error="Unauthorized")

    @staticmethod
    def forbidden() -> None:
        """Нет доступа к избранным пользователя"""

        abort(403, error="Forbidden")

    @staticmethod
    def already_exists() -> None:
        """Данный вопрос уже добавлен в избранные у пользователя"""

        abort(400, error="This question has already been added to the user's favorites")


class FavoriteValidators:
    """Методы для проверки"""

    @staticmethod
    def is_exists(obj: Favorite | Question | None) -> None:
        """Проверка на существование избранного вопроса"""

        if not obj and isinstance(obj, Favorite): FavoriteAborts.favorite_not_found()
        if not obj and isinstance(obj, Question): FavoriteAborts.question_not_found()

    @staticmethod
    def is_available(favorite: Favorite) -> None:
        """Проверка на доступ к избранным"""

        # Проверка на авторизацию пользователя
        if not current_user.is_authenticated: FavoriteAborts.unauthorized()
        # Проверка на доступ к избранному вопросу
        if favorite.user_id != current_user.id: FavoriteAborts.forbidden()
