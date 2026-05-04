"""Ограничение количества запросов. Защита от DDOS, Brute-Force и прочих СПАМ-атак"""

# Безопасность
from flask_limiter import Limiter, RouteLimit
from flask_limiter.util import get_remote_address

# Создание лимитера
limiter: Limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "200 per hour"]
)

# Определение базовых ограничений для API
api_route_limits: list[RouteLimit] = [
    limiter.limit("500 per day"),
    limiter.limit("200 per hour")
]
