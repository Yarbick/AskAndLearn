"""Валидаторы для REST API ресурса"""

# Работа с фреймворком
from flask import request
from flask_login import current_user

# Работа с REST API
import requests
from flask_restful import abort

# Работа с ORM
from qa_node.data.models.question import Question


class QuestionAborts:
    """Методы для вызова ошибок"""

    @staticmethod
    def not_found() -> None:
        """Вопрос не найден"""

        abort(404, error="Question not found")

    @staticmethod
    def unauthorized() -> None:
        """Пользователь не авторизован"""

        abort(403, error="Unauthorized")

    @staticmethod
    def forbidden() -> None:
        """Нет доступа к вопросу"""

        abort(403, error="Forbidden")

    @staticmethod
    def already_exists():
        """Данный вопрос уже существует у пользователя"""

        abort(400, error="The user already has a question with the given title")


class QuestionValidators:
    """Методы для проверки"""

    @staticmethod
    def is_exists(question: Question) -> None:
        """Проверка на существование вопроса"""

        if not question: QuestionAborts.not_found()

    @staticmethod
    def is_available(question: Question) -> None:
        """Проверка на доступ к вопросу"""

        # Проверка на авторизацию пользователя
        if not current_user.is_authenticated: QuestionAborts.unauthorized()
        # Проверка на доступ к вопросу
        if question.creator_id != current_user.id: QuestionAborts.forbidden()
