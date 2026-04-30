"""Инициализация API модуля"""

# Работа с фреймворком
from flask import Blueprint

# Работа с REST API
from flask_restful import Api

# Ресурсы
from .v1.questions.resources import QuestionResource, QuestionListResource

# Создание и настройка Blueprint для API
api_bp = Blueprint(
    f"question_api",
    __name__,
    url_prefix="/api"
)

# Создание и настройка API
api = Api(api_bp)

# Добавление ресурсов
# Ресурсы questions
api.add_resource(QuestionResource, f"/v1/questions/<int:question_id>")
api.add_resource(QuestionListResource, f"/v1/questions")
