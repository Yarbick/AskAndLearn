"""Инициализация API модуля"""

# Работа с фреймворком
from flask import Blueprint

# Безопасность
from security.csrf import api_route_csrf

# Работа с REST API
from flask_restful import Api

# Ресурсы
from .v1.friendships.resources import FriendshipResource, FriendshipListResource

# Создание и настройка Blueprint для API
api_bp: Blueprint = Blueprint(
    f"friendship_api",
    __name__,
    url_prefix="/api"
)

# Создание и настройка API
api: Api = Api(api_bp, decorators=api_route_csrf)

# Добавление ресурсов
# Ресурсы friendships
api.add_resource(FriendshipResource, f"/v1/users/<int:user_id>/friendships/<int:friend_id>")
api.add_resource(FriendshipListResource, f"/v1/users/<int:user_id>/friendships")
