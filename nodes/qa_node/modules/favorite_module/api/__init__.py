"""Инициализация API модуля"""

# Работа с фреймворком
from flask import Blueprint

# Работа с REST API
from flask_restful import Api

# Ресурсы
from .v1.favorites.resources import FavoriteResource, FavoriteListResource

# Создание и настройка Blueprint для API
api_bp = Blueprint(
    f"favorite_api",
    __name__,
    url_prefix="/api"
)

# Создание и настройка API
api = Api(api_bp)

# Добавление ресурсов
# Ресурсы questions
api.add_resource(FavoriteResource, f"/v1/favorites/<int:favorite_id>")
api.add_resource(FavoriteListResource, f"/v1/favorites")
