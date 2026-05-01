"""Валидаторы для REST API ресурса"""
from dbm import error

# Работа с фреймворком
from flask_login import current_user

# Работа с REST API
from flask_restful import abort

# Работа с ORM
from qa_node.data.models.comment import Comment

from qa_node.data.models.question import Question


class CommentAborts:
    """Методы для вызова ошибок"""

    @staticmethod
    def comment_not_found() -> None:
        """Комментарий не найден"""

        abort(404, error="Comment not found")

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
        """Нет доступа к комментарию"""

        abort(403, error="Forbidden")

    @staticmethod
    def question_closed():
        """Вопрос закрыт"""

        abort(400, error="Question closed")


class CommentValidators:
    """Методы для проверки"""

    @staticmethod
    def is_exists(obj: Comment | Question) -> None:
        """Проверка на существование объекта"""

        if not obj:
            if isinstance(obj, Comment): CommentAborts.comment_not_found()
            if isinstance(obj, Question): CommentAborts.question_not_found()

    @staticmethod
    def is_available(comment: Comment) -> None:
        """Проверка на доступ к комментарию"""

        # Проверка на авторизацию пользователя
        if not current_user.is_authenticated: CommentAborts.unauthorized()
        # Проверка на доступ к комментарию
        if comment.creator_id != current_user.id: CommentAborts.forbidden()

    @staticmethod
    def is_question_author(comment: Comment) -> None:

        # Проверка на авторизацию пользователя
        if not current_user.is_authenticated: CommentAborts.unauthorized()
        # Является ли автором вопроса
        if comment.question.creator_id != current_user.id: CommentAborts.forbidden()

    @staticmethod
    def is_question_closed(obj: Comment | Question) -> None:
        """Проверка на закрытие вопроса"""

        if isinstance(obj, Comment) and obj.question.is_closed: CommentAborts.question_closed()
        if isinstance(obj, Question) and obj.is_closed: CommentAborts.question_closed()
