"""Инициализация API модуля"""

# Работа с фреймворком
from flask import Blueprint

# Безопасность
from security.csrf import api_route_csrf

# Работа с REST API
from flask_restful import Api

# Ресурсы
from .v1.favorites.resources import FavoriteResource, FavoriteListResource

# Создание и настройка Blueprint для API
api_bp: Blueprint = Blueprint(
    f"favorite_api",
    __name__,
    url_prefix="/api"
)

# Создание и настройка API
api: Api = Api(api_bp, decorators=api_route_csrf)

# Добавление ресурсов
# Ресурсы favorites
api.add_resource(FavoriteResource, f"/v1/favorites/<int:favorite_id>")
api.add_resource(FavoriteListResource, f"/v1/favorites")
