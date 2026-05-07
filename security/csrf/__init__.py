"""Защита от CSRF атак"""

# Безопасность
from flask_wtf.csrf import CSRFProtect

# Создание объекта для CSRF защиты
csrf_protect: CSRFProtect = CSRFProtect()

# Список декораторов для API-endpoints
api_route_csrf: list = [csrf_protect.exempt]
