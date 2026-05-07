"""Управление кешем приложения"""

# Типизация
from typing import Any


class CacheManager:
    """Класс для управления кешем приложения"""

    storage: dict = {}

    @classmethod
    def set(cls, key: Any, value: Any) -> None:
        """Сохранение данных в кеш"""

        cls.storage[key] = value

    @classmethod
    def get(cls, key: Any, default: Any | None = None) -> Any:
        """Получение данных из кеша"""

        return cls.storage.get(key, default)

    @classmethod
    def delete(cls, key: Any) -> None:
        """Удаление данных из кеша"""

        cls.storage.pop(key)
