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
    def question_not_found() -> None:
        """Вопрос не найден"""

        abort(404, error="Question not found")

    @staticmethod
    def creator_not_found() -> None:
        """Создатель не найден"""

        abort(404, error="Creator not found")

    @staticmethod
    def unauthorized() -> None:
        """Пользователь не авторизован"""

        abort(403, error="Unauthorized")

    @staticmethod
    def forbidden() -> None:
        """Нет доступа к вопросу"""

        abort(403, error="Forbidden")


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

        # Проверка на существование пользователя через REST API
        try:
            # Подготовка данных
            server_address = f"{request.scheme}://{request.host}/api/v1/users/{question.creator_id}"
            # Запрос
            response = requests.get(server_address)

            # Обработка запроса
            if response.status_code == 404: QuestionAborts.creator_not_found()
        except:
            QuestionAborts.creator_not_found()
