"""Инициализация API модуля"""

# Работа с фреймворком
from flask import Blueprint

# Работа с REST API
from flask_restful import Api

# Ресурсы
from .v1.comments.resources import CommentResource, CommentListResource

# Создание и настройка Blueprint для API
api_bp = Blueprint(
    f"comment_api",
    __name__,
    url_prefix="/api"
)

# Создание и настройка API
api = Api(api_bp)

# Добавление ресурсов
# Ресурсы comments
api.add_resource(CommentResource, f"/v1/comments/<int:comment_id>")
api.add_resource(CommentListResource, f"/v1/comments")
