"""Валидаторы для REST API ресурса"""

# Работа с фреймворком
from flask_login import current_user

# Работа с REST API
from flask_restful import abort

# Работа с ORM
from qa_node.data.models.comment import Comment


class CommentAborts:
    """Методы для вызова ошибок"""

    @staticmethod
    def not_found() -> None:
        """Комментарий не найден"""

        abort(404, error="Comment not found")

    @staticmethod
    def unauthorized() -> None:
        """Пользователь не авторизован"""

        abort(403, error="Unauthorized")

    @staticmethod
    def forbidden() -> None:
        """Нет доступа к комментарию"""

        abort(403, error="Forbidden")


class CommentValidators:
    """Методы для проверки"""

    @staticmethod
    def is_exists(comment: Comment) -> None:
        """Проверка на существование комментария"""

        if not comment: CommentAborts.not_found()

    @staticmethod
    def is_available(comment: Comment) -> None:
        """Проверка на доступ к комментарию"""

        # Проверка на авторизацию пользователя
        if not current_user.is_authenticated: CommentAborts.unauthorized()
        # Проверка на доступ к комментарию
        if comment.creator_id != current_user.id: CommentAborts.forbidden()
