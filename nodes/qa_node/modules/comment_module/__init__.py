"""Инициализация модуля Comment"""

# Создание blueprint
from .blueprint import bp
# Подключение обработчиков
from .routes import bp
# Создание API
from .api import api_bp
